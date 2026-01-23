"""
此处（`core/ai/data/models/product_vector.py`）定义了商品实体在AI上下文的向量模型
"""
import json
from datetime import datetime
from typing import List

from sqlalchemy import Integer, String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from core.database.base import Base


class ProductVector(Base):
    """商品向量 ORM 模型"""
    __tablename__ = 'product_vector'

    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 业务相关字段
    product_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, comment="原始商品ID")
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="商品标题")
    description: Mapped[str] = mapped_column(Text, nullable=False, comment="商品描述")

    # 向量字段
    embedding: Mapped[List[float]] = mapped_column(Vector(768), nullable=False, comment="向量数据")

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
