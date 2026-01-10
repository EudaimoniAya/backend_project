"""
配置模块入口，
从这里导入`Settings`类实例以在整个应用中使用配置。
"""
from functools import lru_cache
from .config import Settings


@lru_cache()
def get_settings() -> Settings:
    """获取缓存的配置单例"""
    return Settings()


settings = get_settings()   # 其他模块应该导入的settings对象

__all__ = ['settings', 'Settings']