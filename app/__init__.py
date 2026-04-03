"""Web 应用包：ASGI 入口与 API 分层。"""

from app.main import app, create_app

__all__ = ["app", "create_app"]
