"""路由聚合：子路由挂到 api_router，由 main 统一以 /api 前缀挂载。"""

from fastapi import APIRouter

from app.api import health

api_router = APIRouter()
api_router.include_router(health.router)
