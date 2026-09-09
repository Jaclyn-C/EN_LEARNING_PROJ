"""健康检查路由：验证应用与数据库连通。"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db
from app.schemas.health import HealthOut

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthOut, summary="健康检查")
def health_check(db: Annotated[Session, Depends(get_db)]) -> HealthOut:
    """GET /api/health：执行 SELECT 1 验证 DB；失败返回 503 及错误信息。"""
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"数据库连接失败: {exc}") from exc
    return HealthOut(status="ok", app_env=get_settings().APP_ENV, db="ok")
