"""数据库引擎与会话（SQLite 起步，换 PostgreSQL 只改 DATABASE_URL）。"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

_engine_kwargs = {}
if settings.DATABASE_URL.startswith("sqlite"):
    # FastAPI 多线程访问 SQLite 连接需要放开同线程校验
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, **_engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """全项目 ORM 模型基类。"""


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖：每请求一个会话，请求结束自动关闭。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
