"""LLMClient：全项目唯一的 LLM 调用入口（CLAUDE.md §6、PLAN §5.5）。

- 模型名 / base_url / key 全部来自 `.env`（经 `app.core.config.get_settings`），禁止硬编码；
- 文本与视觉（`vision=True`，messages 的 content 支持 OpenAI 风格的
  `[{"type": "text", ...}, {"type": "image_url", ...}]` 块）两种调用；
- `json_schema` 结构化输出：response_format JSON 模式 + Schema 注入 system 指令 +
  本地 Pydantic / JSON Schema 校验，失败把校验错误回灌给模型重试一次，
  再失败抛 `LLMError`（降级报错），成功返回校验后的 JSON 字符串；
- 每次调用后更新 `self.last_usage`（token 用量）与 `self.last_attempts`（底层调用次数），
- LangSmith 追踪无需本层代码：环境变量 `LANGSMITH_TRACING=true` 时 langchain 自动上报。

结构化输出实现选择（2026-09-09，M0）：
1. 用 `response_format={"type": "json_object"}`（OpenAI 兼容 JSON 模式，智谱 GLM-4
   系列官方支持）+ 把 JSON Schema 写进 system 指令 + 本地校验；
2. 不用 `with_structured_output()`：其默认走 function calling（GLM 各型号工具调用
   遵从度不一，glm-4-flash 等较弱），且封装为一次性调用，无法在重试时把校验错误
   回灌进对话；
3. 不用 `response_format={"type": "json_schema"}`（strict 结构化输出）：OpenAI 专属
   特性，智谱不保证兼容。
方案 1 对 OpenAI 兼容网关的兼容面最广，且校验/重试逻辑完全由我们掌控。
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from typing import Any

from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, ValidationError

from app.core.config import get_settings

DEFAULT_TIMEOUT = 120.0

_JSON_ONLY_PREAMBLE = (
    "你只输出一个 JSON 对象：以 { 开头、以 } 结尾；"
    "不要输出任何解释性文字、前后缀或 Markdown 代码块围栏。"
)

# JSON Schema "type" 关键字 → Python 类型（dict schema 轻量校验用）
_SCHEMA_TYPES: dict[str, tuple[type, ...]] = {
    "string": (str,),
    "number": (int, float),
    "integer": (int,),
    "boolean": (bool,),
    "object": (dict,),
    "array": (list,),
    "null": (type(None),),
}


class LLMError(Exception):
    """LLM 调用失败或结构化输出重试一次后仍未通过校验时的统一降级异常。"""


def _extract_json(text: str) -> Any:
    """从模型回复中提取 JSON：容忍代码块围栏与前后杂文，失败抛 ValueError。"""
    stripped = text.strip()
    fenced = re.match(r"^```(?:json)?\s*(.*?)\s*```$", stripped, re.DOTALL)
    if fenced:
        stripped = fenced.group(1)
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        # 兜底：截取首个 { 到末个 } 之间的片段再试一次
        start, end = stripped.find("{"), stripped.rfind("}")
        if start != -1 and end > start:
            return json.loads(stripped[start : end + 1])
        raise


def _validate_schema(value: Any, schema: dict, path: str = "$") -> list[str]:
    """按 JSON Schema 子集（type/enum/required/properties/items）做轻量校验。

    只覆盖本项目自有 prompt 所用到的特性，返回错误列表（空列表 = 通过）。
    需要完整 JSON Schema 校验时再评估引入 jsonschema 库。
    """
    errors: list[str] = []
    expected = _SCHEMA_TYPES.get(schema.get("type", ""), ())
    if expected and not isinstance(value, expected):
        errors.append(f"{path}: 期望 {schema['type']}，实际 {type(value).__name__}")
    if expected and isinstance(value, bool) and bool not in expected:
        # bool 是 int 子类，显式拒绝把 true/false 当 number/integer
        errors.append(f"{path}: 期望 {schema['type']}，实际 bool")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} 不在 enum {schema['enum']!r} 内")
    if isinstance(value, dict):
        for required in schema.get("required", []):
            if required not in value:
                errors.append(f"{path}: 缺少 required 字段 {required!r}")
        for key, sub in schema.get("properties", {}).items():
            if key in value:
                errors.extend(_validate_schema(value[key], sub, f"{path}.{key}"))
    if isinstance(value, list) and "items" in schema:
        for i, item in enumerate(value):
            errors.extend(_validate_schema(item, schema["items"], f"{path}[{i}]"))
    return errors


def _message_text(message: AIMessage) -> str:
    """AIMessage.content 归一为 str（视觉/多模态回复可能是分块列表）。"""
    content = message.content
    if isinstance(content, str):
        return content
    return "".join(
        part.get("text", "") for part in content if isinstance(part, dict)
    )


class LLMClient:
    """LLM 调用门面：`chat()` 返回模型文本或（结构化模式下）校验后的 JSON 字符串。

    属性（每次 `chat()` 后更新，供脚本读取做 token 记账）：
    - `last_usage`: dict，键 input_tokens / output_tokens / total_tokens；
      结构化调用若发生重试，为两次底层调用之和；
    - `last_attempts`: 最近一次 `chat()` 触发的底层模型调用次数（1 或 2）。
    """

    def __init__(
        self,
        model: str | None = None,
        vision_model: str | None = None,
        *,
        temperature: float | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """`model` / `vision_model` 缺省时读 `.env` 的 LLM_MODEL / LLM_VISION_MODEL。

        `temperature` 缺省 None 表示用模型/网关默认值。选型对比脚本可通过
        `model=` 覆盖来逐个测试候选型号。
        """
        self._model = model
        self._vision_model = vision_model
        self._temperature = temperature
        self._timeout = timeout
        self._llm_cache: dict[tuple[str, bool], Any] = {}
        self.last_usage: dict[str, int] = {}
        self.last_attempts = 0

    # ------------------------------------------------------------------ 对外

    def chat(
        self,
        messages: list[dict],
        json_schema: type[BaseModel] | dict | None = None,
        vision: bool = False,
    ) -> str:
        """调用一次模型。`messages` 为 OpenAI 风格 dict 列表，原样透传（不被修改）。

        - `json_schema`: Pydantic 模型类或 JSON Schema dict 时走结构化输出，
          返回**通过校验后**的 JSON 字符串；否则返回模型纯文本回复；
        - `vision`: True 时用 LLM_VISION_MODEL，content 支持 text/image_url 块。
        """
        settings = get_settings()
        if not settings.ZHIPU_API_KEY:
            raise LLMError("ZHIPU_API_KEY 未配置：请在项目根 .env 填入智谱 API key")
        if not settings.LLM_BASE_URL:
            raise LLMError(
                "LLM_BASE_URL 未配置：智谱 OpenAI 兼容地址为 "
                "https://open.bigmodel.cn/api/paas/v4"
            )
        model = (self._vision_model if vision else self._model) or (
            settings.LLM_VISION_MODEL if vision else settings.LLM_MODEL
        )
        if not model:
            which = "LLM_VISION_MODEL" if vision else "LLM_MODEL"
            raise LLMError(f"{which} 未配置：请在项目根 .env 设置后再调用")

        if json_schema is None:
            llm = self._get_llm(model, json_mode=False)
            text, usage = self._invoke(llm, list(messages), model)
            self.last_usage, self.last_attempts = usage, 1
            return text
        return self._chat_structured(messages, json_schema, model)

    # -------------------------------------------------------------- 内部实现

    def _chat_structured(
        self, messages: list[dict], json_schema: type[BaseModel] | dict, model: str
    ) -> str:
        """结构化输出：JSON 模式调用 + 校验，失败回灌校验错误重试一次。"""
        if isinstance(json_schema, type) and issubclass(json_schema, BaseModel):
            schema_dict: dict = json_schema.model_json_schema()
            pydantic_cls: type[BaseModel] | None = json_schema
        elif isinstance(json_schema, dict):
            schema_dict, pydantic_cls = json_schema, None
        else:
            raise LLMError(
                f"json_schema 需为 Pydantic 模型类或 JSON Schema dict，"
                f"收到 {type(json_schema).__name__}"
            )

        llm = self._get_llm(model, json_mode=True)
        instruction = (
            f"{_JSON_ONLY_PREAMBLE}\n"
            f"输出必须符合如下 JSON Schema（字段名与类型严格一致）：\n"
            f"{json.dumps(schema_dict, ensure_ascii=False)}"
        )
        convo = [dict(m) for m in messages]
        # 只保留一个 system 消息（合并 schema 指令），兼容对多 system 敏感的网关
        if convo and convo[0].get("role") == "system":
            convo[0] = {**convo[0], "content": f"{convo[0]['content']}\n\n{instruction}"}
        else:
            convo.insert(0, {"role": "system", "content": instruction})

        usage_sum = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
        problem, raw_reply = "", ""
        for attempt in (1, 2):
            raw_reply, usage = self._invoke(llm, convo, model)
            for key in usage_sum:
                usage_sum[key] += usage.get(key, 0)
            try:
                parsed = _extract_json(raw_reply)  # JSONDecodeError 是 ValueError 子类
                if pydantic_cls is not None:
                    validated: Any = pydantic_cls.model_validate(parsed).model_dump(mode="json")
                else:
                    errors = _validate_schema(parsed, schema_dict)
                    if errors:
                        raise ValueError("；".join(errors))
                    validated = parsed
            except (ValueError, ValidationError) as exc:
                problem = str(exc)
                convo = [
                    *convo,
                    {"role": "assistant", "content": raw_reply},
                    {
                        "role": "user",
                        "content": (
                            f"你上面的回复未通过 JSON 校验：{problem}\n"
                            f"请修正问题，重新只输出一个符合 Schema 的 JSON 对象。"
                        ),
                    },
                ]
                continue
            self.last_usage, self.last_attempts = usage_sum, attempt
            return json.dumps(validated, ensure_ascii=False)

        self.last_usage, self.last_attempts = usage_sum, 2
        raise LLMError(
            f"结构化输出重试一次后仍未通过校验（model={model}）。\n"
            f"最后一次校验错误：{problem}\n"
            f"模型最后一次原始回复（截断 500 字）：{raw_reply[:500]}"
        )

    def _get_llm(self, model: str, json_mode: bool) -> Any:
        """按 (model, json_mode) 缓存 ChatOpenAI 实例（含绑定的 response_format）。"""
        key = (model, json_mode)
        if key not in self._llm_cache:
            settings = get_settings()
            llm = ChatOpenAI(
                model=model,
                api_key=settings.ZHIPU_API_KEY,
                base_url=settings.LLM_BASE_URL,
                temperature=self._temperature,
                timeout=self._timeout,
            )
            if json_mode:
                # 智谱 GLM-4 系列支持 OpenAI 兼容的 JSON 模式；选择理由见模块 docstring
                llm = llm.bind(response_format={"type": "json_object"})
            self._llm_cache[key] = llm
        return self._llm_cache[key]

    def _invoke(self, llm: Any, messages: list[dict], model: str) -> tuple[str, dict]:
        """发起一次底层调用，返回 (模型文本, token 用量)；网络/鉴权错误统一转 LLMError。"""
        try:
            message = llm.invoke(messages)
        except LLMError:
            raise
        except Exception as exc:  # 网络/鉴权/模型名等一切底层异常统一降级
            raise LLMError(
                f"调用模型 {model} 失败（检查 key/网络/LLM_BASE_URL/模型名）："
                f"{type(exc).__name__}: {exc}"
            ) from exc
        usage = message.usage_metadata or {}
        normalized = {
            "input_tokens": usage.get("input_tokens", 0) or 0,
            "output_tokens": usage.get("output_tokens", 0) or 0,
            "total_tokens": usage.get("total_tokens", 0) or 0,
        }
        return _message_text(message), normalized


@lru_cache
def get_llm_client() -> LLMClient:
    """进程级单例工厂：业务代码统一从这里取客户端（模型配置读 .env）。"""
    return LLMClient()
