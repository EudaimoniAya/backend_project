"""
购物车行：可选极简加购能力。
"""
from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import Integer, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.base import Base

if TYPE_CHECKING:
    from models.user import User
    from models.product import Product


class CartItem(Base):
    __tablename__ = 'cart_items'
    __table_args__ = (
        UniqueConstraint('user_id', 'product_id', name='uq_cart_items_user_product'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True,
                                    comment='购物车行ID')
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False, index=True,
        comment='买家用户ID',
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('products.id', ondelete='CASCADE'),
        nullable=False, index=True,
        comment='商品ID',
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1,
                                          comment='数量')
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False,
        comment='更新时间',
    )

    user: Mapped['User'] = relationship('User', back_populates='cart_items')
    product: Mapped['Product'] = relationship('Product', back_populates='cart_items')

    def __repr__(self) -> str:
        return f'<CartItem(user={self.user_id}, product={self.product_id}, qty={self.quantity})>'
