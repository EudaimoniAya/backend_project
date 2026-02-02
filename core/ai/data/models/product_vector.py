"""
此处（`core/ai/data/models/product_vector.py`）定义了商品实体在AI上下文的向量模型
"""
from datetime import datetime
from typing import List

from sqlalchemy import Integer, String, Text, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from core.database.base import Base


class ProductVector(Base):
    """商品向量 ORM 模型"""
    __tablename__ = 'product_vector'

    # --- 主键 ---
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True,
                                    comment="主键")

    # --- 业务关联 ---
    product_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True,
                                            comment="原始商品id")
    seller_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True,
                                           comment="商家id")

    # --- 内容与块信息 ---
    content: Mapped[str] = mapped_column(Text, nullable=False,
                                         comment="商品描述块")
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0,
                                             comment="描述文本块在原文的顺序索引")

    # --- 元数据（从业务上下文中同步得到） ---
    title: Mapped[str] = mapped_column(String(200), nullable=False,
                                       comment="商品标题")
    category: Mapped[str] = mapped_column(String(100), nullable=False,
                                          comment="分类名称")

    # --- 向量数据 ---
    embedding: Mapped[List[float]] = mapped_column(Vector(768), nullable=False, comment="向量数据")

    # --- 时间戳 ---
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(),
                                                 comment="同步时间，用于增量更新判断")

    __table_args__ = (
        # 复合索引，优化按商品和分类的查询
        Index('idx_product_category', 'product_id', 'category'),
    )
