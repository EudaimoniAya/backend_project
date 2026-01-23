from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    async_scoped_session, AsyncSession)
from asyncio import current_task
from engine import engine

AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,  # 异步环境中通常设为False
    class_=AsyncSession
)

# 3. 使用async_scoped_session确保线程安全
AsyncScopedSession = async_scoped_session(AsyncSessionFactory, scopefunc=current_task)
