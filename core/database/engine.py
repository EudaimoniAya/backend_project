"""
这里将存放应用级的单例 (engine, AsyncSessionLocal)。
它是配置（settings）到具体数据库驱动之间的桥梁，在应用启动时初始化一次。
"""
from asyncio import current_task

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    async_scoped_session, AsyncSession)
from operations.settings import settings


# 1. 创建引擎
engine = create_async_engine(
    settings.session_database_url,
    # 将输出所有执行SQL的日志（默认是关闭的）
    echo=True,
    # 连接池大小（默认是5个）
    pool_size=10,
    # 允许连接池的最大的连接数（默认是10个）
    max_overflow=20,
    # 获得连接超时时间（默认为30s）
    pool_timeout=10,
    # 连接回收时间（默认是-1，代表永不回收）
    pool_recycle=3600,
    # 连接前是否预检查（默认为False）
    pool_pre_ping=True,
)
