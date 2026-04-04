"""
用户收藏商品，唯一约束 (user_id, product_id)。
"""
from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import Integer, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.base import Base

if TYPE_CHECKING:
    from models.user import User
    from models.product import Product


class UserFavorite(Base):
    __tablename__ = 'user_favorites'
    __table_args__ = (
        UniqueConstraint('user_id', 'product_id', name='uq_user_favorites_user_product'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True,
                                    comment='收藏记录ID')
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False, index=True,
        comment='用户ID',
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('products.id', ondelete='CASCADE'),
        nullable=False, index=True,
        comment='商品ID',
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False,
        comment='收藏时间',
    )

    user: Mapped['User'] = relationship('User', back_populates='favorites')
    product: Mapped['Product'] = relationship('Product', back_populates='favorited_by')

    def __repr__(self) -> str:
        return f'<UserFavorite(user={self.user_id}, product={self.product_id})>'
