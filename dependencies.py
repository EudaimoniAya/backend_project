from sqlalchemy.ext.asyncio import AsyncSession
from core.database.session import AsyncScopedSession


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
        AsyncScopedSession.remove()
