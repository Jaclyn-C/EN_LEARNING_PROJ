"""ORM 模型统一出口：新模型必须在此导出，Alembic autogenerate 才能识别。"""

from app.models.user import User

__all__ = ["User"]
