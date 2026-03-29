"""pytest 全局夹具与测试前置环境。"""

import os

# 在导入 `operations.settings` 之前补齐必填环境变量，便于 CI 与本地无 .env 运行测试
_env_defaults: dict[str, str] = {
    "DEEPSEEK_API_KEY": "test",
    "MAIN_DB_PASSWORD": "test",
    "MAIN_DB_NAME": "test",
    "SESSION_DB_PASSWORD": "test",
    "SESSION_DB_NAME": "test",
    "PRODUCT_VECTOR_DB_PASSWORD": "test",
    "PRODUCT_VECTOR_DB_NAME": "test",
}
for _key, _val in _env_defaults.items():
    os.environ.setdefault(_key, _val)

from asyncio import current_task

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

test_url = "sqlite+aiosqlite:///:memory:"


# ------ 测试用数据库相关部分 -------
# 1. 创建引擎
# SQLite 内存库不支持与 MySQL/PG 相同的部分连接池参数，仅保留兼容项
engine = create_async_engine(
    test_url,
    echo=True,
)
AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,  # 异步环境中通常设为False
    class_=AsyncSession,
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
@pytest.fixture(scope="session")
def main_db_manager_in_memory() -> None:
    """占位：后续可改为挂接内存库 AsyncSession 夹具。"""
    pass
