"""
商品向量库（PostgreSQL + pgvector）专用异步引擎。
与 `engine.py` 中会话库分离，供 `ProductVectorStore` 与防腐层同步/检索使用。
"""
from sqlalchemy.ext.asyncio import create_async_engine

from operations.settings import settings

product_vector_engine = create_async_engine(
    settings.product_vector_database_url,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_timeout=10,
    pool_recycle=3600,
    pool_pre_ping=True,
)
