"""
此处（`models/user.py`）定义了传统后端业务的用户模型，它有两种身份：buyer: 买家，seller: 卖家
其中卖家是作为特殊的买家，拥有独有的功能，卖家的用户id作为商品表的外键
"""
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
import enum
from pwdlib import PasswordHash

from sqlalchemy import Integer, String, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database.base import Base

if TYPE_CHECKING:
    from models.product import Product
    from models.shop import Shop
    from models.order import Order
    from models.cart_item import CartItem
    from models.user_favorite import UserFavorite
    from models.product_view import ProductView
    from models.conversation import Conversation, Message

password_hash = PasswordHash.recommended()


class UserRole(enum.Enum):
    """用户角色枚举"""
    BUYER = 'buyer'
    SELLER = 'seller'


class User(Base):
    __tablename__ = 'users'

    # --- 主键 ---
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True,
                                    comment='用户ID')

    # --- 业务信息 ---
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True,
                                          comment='用户名')
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True,
                                       comment='用户邮箱')
    _password: Mapped[str] = mapped_column("password", String(200), nullable=False,
                                           comment='用户密码（加密）')

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        nullable=False,
        default=UserRole.BUYER,
        comment='用户角色：buyer（购买者）/seller（商家）'
    )

    # 心跳或轮询更新，用于在线判断（与阈值组合）
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, index=True,
        comment='最近活跃时间，可空',
    )

    # --- 反向关系 ---
    products: Mapped[List['Product']] = relationship(
        'Product',
        back_populates='seller',  # 对应 Product.seller
        lazy='dynamic',  # 返回查询对象，便于后续过滤和分页
    )
    owned_shop: Mapped[Optional['Shop']] = relationship(
        'Shop',
        back_populates='owner',
        uselist=False,
    )
    orders: Mapped[List['Order']] = relationship(
        'Order',
        back_populates='buyer',
        lazy='dynamic',
    )
    cart_items: Mapped[List['CartItem']] = relationship(
        'CartItem',
        back_populates='user',
        lazy='dynamic',
    )
    favorites: Mapped[List['UserFavorite']] = relationship(
        'UserFavorite',
        back_populates='user',
        lazy='dynamic',
    )
    product_views: Mapped[List['ProductView']] = relationship(
        'ProductView',
        back_populates='user',
        lazy='dynamic',
    )
    conversations_as_buyer: Mapped[List['Conversation']] = relationship(
        'Conversation',
        back_populates='buyer',
        lazy='dynamic',
    )
    messages_sent: Mapped[List['Message']] = relationship(
        'Message',
        back_populates='sender_user',
        lazy='dynamic',
    )

    def __init__(self, *args, **kwargs):
        password = kwargs.pop('password', None)
        super().__init__(*args, **kwargs)
        if password:
            # 使用FastAPI推荐的第三方库pwdlib加密，
            # 这里的self.password赋值操作会调用@password.setter装饰的方法
            self.password = password

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw_password):
        self._password = password_hash.hash(raw_password)

    def verify_password(self, raw_password):
        # 这里的self.password会调用@property修饰的方法，直接获取到self._password
        return password_hash.verify(raw_password, self.password)

    def __repr__(self):
        return f'<User(id={self.id}, username="{self.username}", role={self.role.value})>'
