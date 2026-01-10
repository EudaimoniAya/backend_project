import atexit
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

        # 程序退出时自动释放所有处理器
        atexit.register(self.close)

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
        """函数调用日志装饰器，用于自动记录函数执行情况、耗时和异常"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            """func为被装饰器装饰的函数"""
            func_name = func.__name__       # 函数名
            module_name = func.__module__   # 模块名

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
        """
            关闭所有日志处理器，释放文件锁
            Windows的文件锁定很严格，在没有close()时，文件如果被打开被锁定的话，即使程序结束后，文件仍可能锁定几秒
            而有close()方法时，可以通过调用它显式地立即释放文件锁
        """
        # 如果已经关闭，直接返回
        if not self._handler_ids:
            return

        # 记录要移除的处理器ID
        handler_ids_to_remove = list(self._handler_ids)

        # 先清空列表，避免重复操作
        self._handler_ids.clear()

        # 尝试移除每个处理器
        for handler_id in handler_ids_to_remove:
            try:
                loguru_logger.remove(handler_id)
            except ValueError as e:
                # 处理器已经被移除的情况，这是预期的
                # 可以静默处理，不打印异常
                if "no existing handler" not in str(e):
                    # 如果是其他ValueError，打印
                    print(f"移除处理器 {handler_id} 时出现异常: {e}")
            except Exception as e:
                # 其他异常，打印日志
                print(f"移除处理器 {handler_id} 时出现未知异常: {e}")

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
