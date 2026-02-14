import pytest
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    async_scoped_session, AsyncSession)
from asyncio import current_task
from fastapi import Depends

test_url = "sqlite:///:memory:"


# ------ 测试用数据库相关部分 -------
# 1. 创建引擎
engine = create_async_engine(
    test_url,
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
AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,  # 异步环境中通常设为False
    class_=AsyncSession
)

# 3. 使用async_scoped_session确保线程安全
AsyncScopedSession = async_scoped_session(AsyncSessionFactory, scopefunc=current_task)



async def get_session() -> AsyncSession:
    session = AsyncScopedSession()
    try:
        yield session
        # await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
        await AsyncScopedSession.remove()


# ------ 夹具部分 ------
@pytest.fixture(scope='session')
def main_db_manager_in_memory(
        session: AsyncSession = Depends(get_session),
):
    pass
