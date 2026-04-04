"""
极简订单：支撑购买历史展示与推荐信号，不含支付状态机。
"""
from typing import TYPE_CHECKING, List
from datetime import datetime
import enum

from sqlalchemy import Integer, String, DateTime, ForeignKey, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.base import Base

if TYPE_CHECKING:
    from models.user import User
    from models.shop import Shop
    from models.product import Product


class OrderStatus(str, enum.Enum):
    """订单极简状态"""
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    PLACED = 'placed'


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True,
                                    comment='订单ID')
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False, index=True,
        comment='买家用户ID',
    )
    shop_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('shops.id', ondelete='RESTRICT'),
        nullable=False, index=True,
        comment='店铺ID',
    )
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, native_enum=False, length=32),
        nullable=False,
        default=OrderStatus.COMPLETED,
        comment='订单状态：placed/completed/cancelled',
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, index=True,
        comment='创建时间',
    )

    buyer: Mapped['User'] = relationship('User', back_populates='orders')
    shop: Mapped['Shop'] = relationship('Shop', back_populates='orders')
    items: Mapped[List['OrderItem']] = relationship(
        'OrderItem', back_populates='order', cascade='all, delete-orphan',
    )

    def __repr__(self) -> str:
        return f'<Order(id={self.id}, user={self.user_id}, status={self.status})>'


class OrderItem(Base):
    __tablename__ = 'order_items'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True,
                                    comment='订单行ID')
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('orders.id', ondelete='CASCADE'),
        nullable=False, index=True,
        comment='订单ID',
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('products.id', ondelete='RESTRICT'),
        nullable=False, index=True,
        comment='商品ID',
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, comment='数量')
    unit_price_snapshot: Mapped[int] = mapped_column(
        Integer, nullable=False,
        comment='成交单价快照，单位：分',
    )

    order: Mapped['Order'] = relationship('Order', back_populates='items')
    product: Mapped['Product'] = relationship('Product', back_populates='order_items')

    def __repr__(self) -> str:
        return f'<OrderItem(order={self.order_id}, product={self.product_id}, qty={self.quantity})>'
