# repository/category_repository.py
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List

from models.category import Category
from schemas.category import CategoryCreateSchema, CategoryUpdateSchema


class CategoryRepository:
    """分类仓储层"""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ========== 查询方法 ==========

    async def get_by_id(self, category_id: int, include_products: bool = False) -> Optional[Category]:
        """根据ID获取分类"""
        stmt = select(Category).where(Category.id == category_id)

        if include_products:
            stmt = stmt.options(selectinload(Category.products))

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Category]:
        """根据名称获取分类"""
        stmt = select(Category).where(Category.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, include_products: bool = False) -> List[Category]:
        """获取所有分类"""
        stmt = select(Category).order_by(Category.name)

        if include_products:
            stmt = stmt.options(selectinload(Category.products))

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def exists(self, category_id: int) -> bool:
        """检查分类是否存在"""
        stmt = select(Category.id).where(Category.id == category_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def name_exists(self, name: str, exclude_id: Optional[int] = None) -> bool:
        """检查分类名称是否已存在"""
        conditions = [Category.name == name]
        if exclude_id:
            conditions.append(Category.id != exclude_id)

        stmt = select(Category.id).where(*conditions)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    # ========== 创建与更新 ==========

    async def create(self, category_data: CategoryCreateSchema) -> Category:
        """创建新分类"""
        category = Category(**category_data.model_dump())
        self.session.add(category)

        await self.session.flush()
        await self.session.refresh(category)

        return category

    async def update(self, category_id: int, update_data: CategoryUpdateSchema) -> Optional[Category]:
        """更新分类信息"""
        category = await self.get_by_id(category_id)
        if not category:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(category, key, value)

        await self.session.flush()
        await self.session.refresh(category)

        return category

    # ========== 删除方法 ==========

    async def delete(self, category_id: int) -> bool:
        """删除分类（有商品关联时无法删除，外键约束为RESTRICT）"""
        try:
            stmt = delete(Category).where(Category.id == category_id)
            result = await self.session.execute(stmt)
            return result.rowcount > 0
        except Exception:
            # 捕获外键约束错误，说明有商品在使用该分类
            return False

    # ========== 搜索方法 ==========

    async def search(self, keyword: str) -> List[Category]:
        """搜索分类（按名称模糊匹配）"""
        stmt = select(Category).where(Category.name.ilike(f"%{keyword}%"))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
