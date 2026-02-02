"""
此处（`models/user.py`）定义了传统后端业务的用户模型，它有两种身份：buyer: 买家，seller: 卖家
其中卖家是作为特殊的买家，拥有独有的功能，卖家的用户id作为商品表的外键
"""
from typing import List, TYPE_CHECKING
import enum
from pwdlib import PasswordHash

from sqlalchemy import Integer, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database.base import Base

if TYPE_CHECKING:
    from models.product import Product

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
                                           comment='用户密码')

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        nullable=False,
        default=UserRole.BUYER,
        comment='用户角色：buyer（购买者）/seller（商家）'
    )

    # --- 反向关系 ---
    products: Mapped[List['Product']] = relationship(
        'Product',
        back_populates='seller',  # 对应 Product.seller
        lazy='dynamic',  # 返回查询对象，便于后续过滤和分页
    )

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        password = kwargs.pop('password', None)
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
