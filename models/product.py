"""
此处（`models/product.py`）定义了传统后端业务的商品模型，它存在两个限界上下文：
* 这里定义的ORM模型与MySQL数据库交互，作为商品的业务上下文；
* `core/ai/data/models/product_vector.py`定义的向量模型与Pg数据库交互，作为商品的AI上下文。
"""
from datetime import datetime

from sqlalchemy import Integer, String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from core.database.base import Base


class Product(Base):
    __tablename__ = 'product'

    # 业务相关字段（传给AI上下文）
    id: Mapped[int] = mapped_column(Integer, primary_key=True, auto_increment=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="商品标题")
    description: Mapped[str] = mapped_column(Text, nullable=False, comment="商品描述")
    category: Mapped[str] = mapped_column(String(100), nullable=False, comment="商品分类")

    # 业务相关字段（独有）
    status: Mapped[str] = mapped_column(String(100), nullable=False, comment="用于业务状态控制：上架/下架")
    seller_id: Mapped[int] = mapped_column(Integer, ForeignKey('seller.id'), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False, comment="商品价格")
    stock: Mapped[int] = mapped_column(Integer, nullable=False, comment="商品库存")

    # 元数据
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
