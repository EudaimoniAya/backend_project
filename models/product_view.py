"""
商品浏览事件，供推荐与行为分析；可后续由任务裁剪为最近 N 条。
"""
from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.base import Base

if TYPE_CHECKING:
    from models.user import User
    from models.product import Product


class ProductView(Base):
    __tablename__ = 'product_views'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True,
                                    comment='浏览记录ID')
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
    viewed_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, index=True,
        comment='浏览时间',
    )

    user: Mapped['User'] = relationship('User', back_populates='product_views')
    product: Mapped['Product'] = relationship('Product', back_populates='views')

    def __repr__(self) -> str:
        return f'<ProductView(user={self.user_id}, product={self.product_id})>'
