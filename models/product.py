"""
此处（`models/product.py`）定义了传统后端业务的商品模型，它存在两个限界上下文：
* 这里定义的ORM模型与MySQL数据库交互，作为商品的业务上下文；
* `core/ai/data/models/product_vector.py`定义的向量模型与Pg数据库交互，作为商品的AI上下文。
"""
from typing import TYPE_CHECKING, List
from datetime import datetime

from sqlalchemy import Integer, String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database.base import Base

if TYPE_CHECKING:
    from models.category import Category
    from models.user import User
    from models.shop import Shop
    from models.order import OrderItem
    from models.cart_item import CartItem
    from models.user_favorite import UserFavorite
    from models.product_view import ProductView


class Product(Base):
    __tablename__ = 'products'

    # --- 主键 ---
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True,
                                    comment="商品id")

    # --- 核心属性（同步至AI上下文）---
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True, comment="商品标题")
    description: Mapped[str] = mapped_column(Text, nullable=False, comment="商品描述")
    # 此处使用分类表，AI上下文中则存储完整的类别名
    category_id: Mapped[int] = mapped_column(Integer,
                                             ForeignKey('categories.id', ondelete='RESTRICT'),
                                             nullable=False, index=True,
                                             comment="商品分类表id")

    # --- 交易属性（业务上下文独有）---
    price: Mapped[int] = mapped_column(Integer, nullable=False, comment="商品价格，单位：分")
    stock: Mapped[int] = mapped_column(Integer, nullable=False, comment="商品库存")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='draft',
                                        comment="用于业务状态控制：草稿draft、上架active、下架inactive、缺货out_of_stock")

    # --- 关系属性 ---
    seller_id: Mapped[int] = mapped_column(Integer,
                                           ForeignKey('users.id', ondelete='CASCADE'),
                                           nullable=False, index=True,
                                           comment="商品所属商家id")
    shop_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('shops.id', ondelete='RESTRICT'),
        nullable=False, index=True,
        comment="商品所属店铺id，与卖家店铺一致，由应用层与 seller 对齐",
    )

    # --- 时间戳 ---
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(),
                                                 index=True, onupdate=func.now())

    # --- ORM关系（正向频繁访问用joined，反向大量数据用dynamic） ---
    category: Mapped['Category'] = relationship('Category',
                                                back_populates='products',
                                                lazy='joined')
    seller: Mapped['User'] = relationship('User',
                                          back_populates='products',
                                          lazy='joined')
    shop: Mapped['Shop'] = relationship('Shop', back_populates='products', lazy='joined')
    order_items: Mapped[List['OrderItem']] = relationship(
        'OrderItem', back_populates='product', lazy='dynamic',
    )
    cart_items: Mapped[List['CartItem']] = relationship(
        'CartItem', back_populates='product', lazy='dynamic',
    )
    favorited_by: Mapped[List['UserFavorite']] = relationship(
        'UserFavorite', back_populates='product', lazy='dynamic',
    )
    views: Mapped[List['ProductView']] = relationship(
        'ProductView', back_populates='product', lazy='dynamic',
    )

    def __repr__(self):
        return (f'<Product(id={self.id}, title="{self.title}, seller={self.seller_id}"'
                f'category_id={self.category_id}, price={self.price}, status={self.status})>')
