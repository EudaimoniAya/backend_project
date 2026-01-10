"""
日志模块入口
在此处导入`SimpleLogger`类的实例以及日志装饰器
"""
from functools import lru_cache
from pathlib import Path
from typing import Optional
from .logger import SimpleLogger


@lru_cache(maxsize=None)
def get_logger(log_dir: Optional[Path] = None) -> SimpleLogger:
    """
    获取日志实例（单例模式）

    Args:
        log_dir: 日志目录，仅在第一次调用时生效

    Returns:
        SimpleLogger实例
    """
    return SimpleLogger(log_dir=log_dir)


# 初始化默认日志实例（使用默认配置）
_default_logger_instance = get_logger()

# 导出用户需要的API
logger = _default_logger_instance.logger
log_func = SimpleLogger.log_func

__all__ = ['logger', 'log_func']
