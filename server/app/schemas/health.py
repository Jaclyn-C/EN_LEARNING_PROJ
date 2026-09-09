"""健康检查出入参。"""

from pydantic import BaseModel


class HealthOut(BaseModel):
    status: str
    app_env: str
    db: str
