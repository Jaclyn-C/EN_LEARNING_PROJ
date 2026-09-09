"""通用依赖：取当前用户的唯一入口（多用户预留，未来加认证只改这里）。"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.user import User


def get_current_user(db: Annotated[Session, Depends(get_db)]) -> User:
    """单用户阶段固定返回默认用户（id=1，不存在则惰性创建）。"""
    user = db.get(User, 1)
    if user is None:
        user = User(name="默认用户", email="default@enlearning.local")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
