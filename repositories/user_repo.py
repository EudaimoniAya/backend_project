from typing import Optional, List
from sqlalchemy import select, update, delete, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.orm import selectinload

from models.user import User, UserRole
from schemas.user import UserCreateSchema  # 需要你创建的Pydantic模型


class UserRepository:
    """用户仓储层，采用现代异步上下文管理器和类型安全设计"""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ========== 查询方法 ==========

    async def get_by_id(self, user_id: int) -> User | None:
        """根据ID获取用户，包含关联的商品（用于商家）"""
        # 使用 session.get() 更简洁，但需要手动加载关系
        # 这里使用 select + join 一次性加载所有常用关联数据
        stmt = (
            select(User)
            .options(selectinload(User.products))  # 预加载商品关系
            .where(User.id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """根据邮箱获取用户（用于登录）"""
        # session.get() 只能按主键查询，所以这里用 select
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """根据用户名获取用户"""
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """检查邮箱是否已存在（用于注册验证）"""
        stmt = select(exists().where(User.email == email))
        result = await self.session.execute(stmt)
        return result.scalar()

    # ========== 业务方法 ==========

    async def create_user(self, user_data: UserCreateSchema) -> User:
        """创建新用户（支持注册时直接设置角色）"""
        # 将Pydantic模型转换为ORM模型
        user_dict = user_data.model_dump()
        user = User(**user_dict)

        self.session.add(user)
        await self.session.flush()  # 获取生成的ID，但不提交事务
        await self.session.refresh(user)  # 刷新以获取数据库默认值
        return user

    async def create_seller(self, user_data: UserCreateSchema) -> User:
        """创建商家用户（设置角色为SELLER）"""
        # 确保创建的是商家
        user_dict = user_data.model_dump()
        user_dict['role'] = UserRole.SELLER
        user = User(**user_dict)

        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def update_user(self, user_id: int, update_data: dict) -> User | None:
        """更新用户信息（部分更新）"""
        user = await self.get_by_id(user_id)
        if not user:
            return None

        for key, value in update_data.items():
            if hasattr(user, key) and key != 'id':  # 防止修改ID
                setattr(user, key, value)

        # updated_at 会自动更新（因为定义了onupdate=func.now()）
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def delete_user(self, user_id: int) -> bool:
        """删除用户（会级联删除其商品）"""
        user = await self.get_by_id(user_id)
        if not user:
            return False

        await self.session.delete(user)
        await self.session.flush()
        return True

    # ========== 业务验证方法 ==========

    async def is_seller(self, user_id: int) -> bool:
        """验证用户是否为商家（用于权限控制）"""
        stmt = select(User.role).where(User.id == user_id)
        result = await self.session.execute(stmt)
        role = result.scalar_one_or_none()
        return role == UserRole.SELLER if role else False

    async def get_seller_products(self, seller_id: int):
        """获取商家的所有商品（利用反向关系的dynamic特性）"""
        user = await self.get_by_id(seller_id)
        if not user or user.role != UserRole.SELLER:
            return None

        # 因为User.products是lazy='dynamic'，所以这里返回的是查询对象
        # 可以在服务层进一步过滤、分页
        return user.products
