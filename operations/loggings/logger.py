import sys
from pathlib import Path
from functools import wraps
from loguru import logger as loguru_logger
import time


class SimpleLogger(object):
    """简单日志管理器类"""
    def __init__(self, log_dir: Path | None = None):
        """
        初始化日志管理器
        Args:
            log_dir: 日志目录路径，默认为“logs”
        """
        # 确保日志目录存在
        self.log_dir = log_dir or Path("logs")
        self.log_dir.mkdir(exist_ok=True)

        # 保存处理器ID以便后续关闭
        self._handler_ids = []

        # 移除loguru默认处理器
        loguru_logger.remove()

        # 设置各种处理器
        self._setup_console()
        self._setup_file_logging()
        self._setup_error_logging()

        # 打印初始化信息
        loguru_logger.info("日志系统初始化完成")
        loguru_logger.info(f"日志文件保存在: {self.log_dir.absolute()}")

    def _setup_console(self):
        """设置控制台日志输出"""
        console_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        handler_id = loguru_logger.add(
            sys.stderr,
            format=console_format,
            level="INFO",
            colorize=True,
            backtrace=True,
            diagnose=False
        )
        self._handler_ids.append(handler_id)

    def _setup_file_logging(self):
        """设置文件日志输出"""
        file_format = (
            "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
            "{name}:{function}:{line} | {message}"
        )
        handler_id = loguru_logger.add(
            self.log_dir / "app_{time:YYYY-MM-DD}.log",
            format=file_format,
            level="DEBUG",
            rotation="00:00",
            retention="7 days",
            compression="zip",
            encoding="utf-8",
            enqueue=True
        )
        self._handler_ids.append(handler_id)

    def _setup_error_logging(self):
        """设置错误日志单独输出"""
        error_format = (
            "{time:YYYY-MM-DD HH:mm:ss} | {level} | "
            "{name}:{function}:{line} | {message}\n"
            "Exception: {exception}"
        )

        handler_id = loguru_logger.add(
            self.log_dir / "error_{time:YYYY-MM-DD}.log",
            format=error_format,
            level="ERROR",
            rotation="00:00",
            retention="30 days",
            compression="zip",
            enqueue=True
        )
        self._handler_ids.append(handler_id)

    @staticmethod
    def log_func(func):
        """函数调用日志装饰器"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            module_name = func.__module__

            start_time = time.time()
            loguru_logger.debug(f"开始执行函数: {module_name}.{func_name}")
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time

                loguru_logger.debug(
                    f"函数执行完成: {module_name}.{func_name} | "
                    f"耗时: {execution_time:.3f}秒"
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                loguru_logger.error(
                    f"函数执行失败: {module_name}.{func_name} | "
                    f"耗时: {execution_time:.3f}秒 | "
                    f"异常: {type(e).__name__}: {str(e)}"
                )
                raise
        return wrapper

    def close(self):
        """关闭所有日志处理器，释放文件锁"""
        for handler_id in self._handler_ids:
            try:
                loguru_logger.remove(handler_id)
            except Exception as e:
                # 静默处理，避免干扰正常流程
                pass
        self._handler_ids.clear()

    def __enter__(self):
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时自动关闭"""
        self.close()

    @property
    def logger(self):
        """获取配置好的loguru logger实例"""
        return loguru_logger
