# models/user.py
import enum
from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database.base import Base

if TYPE_CHECKING:
    from .product import Product  # 用于类型提示，避免循环导入


class UserRole(enum.Enum):
    """用户角色枚举"""
    BUYER = 'buyer'
    MERCHANT = 'merchant'


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='用户ID')
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True, comment='用户名')
    # 此处应还有 password_hash, email 等字段，为简洁省略

    # 核心：角色字段
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        nullable=False,
        default=UserRole.BUYER,
        comment='用户角色：buyer（购买者）/merchant（商家）'
    )

    # 反向关系：作为商家时，拥有的商品列表
    products: Mapped[List['Product']] = relationship(
        'Product',
        back_populates='seller',  # 对应 Product.seller
        lazy='dynamic',  # 返回查询对象，便于后续过滤和分页
        cascade='all, delete-orphan'  # 可选：用户删除时，其商品如何处理
    )

    def __repr__(self):
        return f'<User(id={self.id}, username="{self.username}", role={self.role.value})>'