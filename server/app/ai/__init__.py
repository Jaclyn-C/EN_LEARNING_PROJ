"""LLM 抽象层门面（PLAN §5.5）：业务代码只从这里取 `LLMClient` / `load_prompt`。

所有模型调用必须经 `LLMClient`（模型名/base_url/key 读 `.env`，经 langchain-openai
的 ChatOpenAI 直连智谱 GLM）；prompt 一律模板文件放 `server/prompts/` 由
`load_prompt` 渲染。禁止在 `ai/` 之外出现模型调用或内联大段 prompt。
"""

from app.ai.llm_client import LLMClient, LLMError, get_llm_client
from app.ai.prompt_loader import load_prompt

__all__ = ["LLMClient", "LLMError", "get_llm_client", "load_prompt"]
