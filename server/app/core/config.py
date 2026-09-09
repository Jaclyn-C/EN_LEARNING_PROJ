"""应用配置：统一经 pydantic-settings 读取项目根 `.env`（密钥只进 .env）。"""

from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# 项目根：server/app/core/config.py 上溯三级
PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = PROJECT_ROOT / ".env"

# LangSmith SDK 只读进程环境变量：模块导入时把根 .env 载入 os.environ。
# override=False：不覆盖已存在的环境变量（保留测试/部署注入的值）。
load_dotenv(ENV_FILE, override=False)


class Settings(BaseSettings):
    """全局配置。LLM 相关字段仅承载配置，实际调用在 `app/ai/`。"""

    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore")

    # 应用
    APP_ENV: str = "dev"
    DATABASE_URL: str = "sqlite:///./enlearning.db"  # 相对 CWD（约定从 server/ 启动）
    UPLOAD_DIR: str = "uploads"  # 相对 CWD（server/）

    # LLM（智谱 GLM，OpenAI 兼容协议）
    ZHIPU_API_KEY: str = ""
    LLM_BASE_URL: str = ""
    LLM_MODEL: str = ""
    LLM_VISION_MODEL: str = ""

    # LangSmith 调用追踪
    LANGSMITH_TRACING: bool = False
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_PROJECT: str = "en-learning"


@lru_cache
def get_settings() -> Settings:
    """返回单例 Settings；测试注入环境变量后可用 `get_settings.cache_clear()` 重置。"""
    return Settings()
