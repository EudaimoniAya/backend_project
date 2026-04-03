"""聚合`app.api.v1.routes`下的 v1 子路由。"""

from fastapi import APIRouter

from app.api.v1.routes import health

api_router = APIRouter()
api_router.include_router(health.router)

__all__ = ["api_router"]
