"""FastAPI 应用入口：组装异常处理与版本化路由。"""

from fastapi import FastAPI

from app.api.exception_handlers import register_exception_handlers
from app.api.v1.router import api_router
from operations.settings import settings


def create_app() -> FastAPI:
    """构建并返回配置完成的 ASGI 应用（便于测试与多实例部署）。"""
    application = FastAPI(
        title=settings.project_name,
        debug=settings.debug,
    )
    register_exception_handlers(application)
    application.include_router(api_router, prefix=settings.api_v1_str)
    return application


# 创建应用实例，已经添加了异常处理和版本化路由（/api/v1）
app = create_app()

__all__ = ["app", "create_app"]
