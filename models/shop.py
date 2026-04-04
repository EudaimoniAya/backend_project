"""
店铺模型：RAG 与客服按店隔离；v1.0 约定每个卖家至多一家店（owner_user_id 唯一）。
"""
from typing import TYPE_CHECKING, List, Optional
from datetime import datetime

from sqlalchemy import Integer, String, Text, Boolean, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.base import Base

if TYPE_CHECKING:
    from models.user import User
    from models.product import Product
    from models.order import Order
    from models.conversation import Conversation


class Shop(Base):
    """店铺表"""
    __tablename__ = 'shops'
    __table_args__ = (
        UniqueConstraint('owner_user_id', name='uq_shops_owner_user_id'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True,
                                    comment='店铺ID')
    owner_user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment='店主用户ID（卖家）',
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment='店铺名称')
    slug: Mapped[Optional[str]] = mapped_column(
        String(100), unique=True, nullable=True, index=True,
        comment='店铺短链标识，可选',
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment='店铺描述')
    # True 表示优先人工客服；与 last_seen_at 等组合由业务层解析
    manual_first: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default='1',
        comment='是否优先人工接待',
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False,
        comment='创建时间',
    )

    owner: Mapped['User'] = relationship('User', back_populates='owned_shop')
    products: Mapped[List['Product']] = relationship(
        'Product', back_populates='shop', lazy='dynamic',
    )
    orders: Mapped[List['Order']] = relationship(
        'Order', back_populates='shop', lazy='dynamic',
    )
    conversations: Mapped[List['Conversation']] = relationship(
        'Conversation', back_populates='shop', lazy='dynamic',
    )

    def __repr__(self) -> str:
        return f'<Shop(id={self.id}, name="{self.name}", owner={self.owner_user_id})>'
