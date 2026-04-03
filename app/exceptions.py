"""应用层业务异常，供路由与服务抛出，由全局异常处理器转为统一 JSON 响应。"""


class AppException(Exception):
    """可映射为 HTTP 状态码的业务异常。"""

    def __init__(
        self,
        message: str,
        *,
        status_code: int = 400,
        code: str = "app_error",
        detail: dict | list | str | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.code = code
        self.detail = detail
        super().__init__(message)


__all__ = ["AppException"]
