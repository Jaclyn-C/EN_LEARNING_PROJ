#!/usr/bin/env python
"""M0 冒烟脚本：验证 LLMClient 连通智谱 GLM（普通对话 + json_schema 结构化输出）。

用法（在 server/ 目录）：
    .venv/bin/python scripts/test_llm.py [--topic ...] [--word ...]

- ZHIPU_API_KEY 未配置或仍是占位符（sk-xxx）时：打印指引并以非 0 退出码结束，
  不发起任何模型调用；
- key 有效时依次做两次真实调用并打印回复与 token 用量，最后汇总总消耗
  （PLAN §7 纪律：token 消耗记录在测试脚本输出里）；
- 任何调用失败：打印异常与排查建议（key / 网络 / 模型名），退出码非 0。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pydantic import BaseModel

# 让 `app` 包可导入（脚本位于 server/scripts/ 下，server/ 是包根）
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ai import get_llm_client, load_prompt  # noqa: E402
from app.core.config import get_settings  # noqa: E402

KEY_GUIDANCE = """
[跳过真实调用] ZHIPU_API_KEY 未配置或仍是占位符（sk-xxx）。
请编辑项目根 /Users/jaclyn/Desktop/ESG-proj/EN-learning/.env 中的 ZHIPU_API_KEY= 一行
（约第 3 行），填入智谱 API key 后重跑本脚本。
key 获取：https://open.bigmodel.cn/ → 右上角控制台 → API Keys。
"""

TROUBLESHOOT = """
排查建议：
- 鉴权失败（401 / invalid api key）：检查 .env 的 ZHIPU_API_KEY 是否完整、是否为智谱 key；
- 超时 / 连接失败：检查网络，以及 .env 的 LLM_BASE_URL（应为 https://open.bigmodel.cn/api/paas/v4）；
- 模型不存在（model not found / 1211）：检查 .env 的 LLM_MODEL 是否为智谱在售型号
  （https://open.bigmodel.cn/modelcenter 查询）；
- 余额不足 / 限流：到智谱控制台查看 token 余量与并发限制。
"""


class WordCard(BaseModel):
    """smoke_json.md 的输出契约（与模板字段一一对应）。"""

    word: str
    phonetic: str
    meaning: str
    example: str


def _key_problem(key: str) -> bool:
    """key 为空或仍是占位符 sk-xxx 时视为不可用。"""
    return not key or key.strip().startswith("sk-xxx")


def _print_usage(tag: str, usage: dict[str, int]) -> None:
    print(
        f"[tokens] {tag}: input={usage.get('input_tokens', 0)} "
        f"output={usage.get('output_tokens', 0)} total={usage.get('total_tokens', 0)}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="M0 LLM 冒烟：普通对话 + 结构化输出各一次")
    parser.add_argument("--topic", default="spaced repetition in English learning",
                        help="冒烟对话的主题（默认：spaced repetition in English learning）")
    parser.add_argument("--word", default="resilient", help="冒烟查词的单词（默认：resilient）")
    args = parser.parse_args()

    settings = get_settings()
    if _key_problem(settings.ZHIPU_API_KEY):
        print(KEY_GUIDANCE)
        return 1

    client = get_llm_client()
    total = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}

    try:
        # 1) 普通对话：prompt 模板 + LLMClient
        print("=" * 60)
        print(f"[1/2] 普通对话（模板 m0/smoke_chat.md，model={settings.LLM_MODEL}）")
        reply = client.chat(
            [{"role": "user", "content": load_prompt("m0/smoke_chat.md", topic=args.topic)}]
        )
        print(f"回复：{reply}")
        _print_usage("smoke_chat", client.last_usage)
        for key in total:
            total[key] += client.last_usage.get(key, 0)

        # 2) json_schema 结构化输出：解析 + Pydantic 校验 + 失败自动重试一次
        print("=" * 60)
        print(f"[2/2] 结构化输出（模板 m0/smoke_json.md，word={args.word}）")
        raw = client.chat(
            [{"role": "user", "content": load_prompt("m0/smoke_json.md", word=args.word)}],
            json_schema=WordCard,
        )
        card = WordCard.model_validate(json.loads(raw))
        print(f"校验后的 WordCard：{card.model_dump()}")
        _print_usage(f"smoke_json（底层调用 {client.last_attempts} 次）", client.last_usage)
        for key in total:
            total[key] += client.last_usage.get(key, 0)
    except Exception as exc:  # 脚本顶层兜底：打印异常与排查建议后非 0 退出
        print(f"\n[失败] {type(exc).__name__}: {exc}")
        print(TROUBLESHOOT)
        return 1

    # 3) 汇总 token 消耗
    print("=" * 60)
    print(
        f"[汇总] 本次总 token 消耗：input={total['input_tokens']} "
        f"output={total['output_tokens']} total={total['total_tokens']}"
    )

    # 4) LangSmith 提示（tracing 由环境变量驱动，langchain 自动上报，无需代码支持）
    if settings.LANGSMITH_TRACING:
        print(
            f"[LangSmith] LANGSMITH_TRACING=true：去 https://smith.langchain.com "
            f"项目 {settings.LANGSMITH_PROJECT} 查看本次调用 trace。"
        )
    print("[OK] 冒烟通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
