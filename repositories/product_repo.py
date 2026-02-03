# repository/product_repository.py
from sqlalchemy import select, and_, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List

from models.product import Product
from models.user import User, UserRole
from schemas.product import ProductCreateSchema, ProductUpdateSchema


class ProductRepository:
    """商品仓储层"""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ========== 查询方法 ==========

    async def get_by_id(self, product_id: int, include_relations: bool = True) -> Optional[Product]:
        """根据ID获取商品"""
        stmt = select(Product).where(Product.id == product_id)

        if include_relations:
            stmt = stmt.options(
                selectinload(Product.category),
                selectinload(Product.seller)
            )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_seller(self, seller_id: int,
                            status: Optional[str] = None,
                            category_id: Optional[int] = None) -> List[Product]:
        """获取商家的商品列表（支持按状态和分类过滤）"""
        conditions = [Product.seller_id == seller_id]

        if status:
            conditions.append(Product.status == status)
        if category_id:
            conditions.append(Product.category_id == category_id)

        stmt = (
            select(Product)
            .where(and_(*conditions))
            .order_by(Product.updated_at.desc())
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_active_products(self,
                                  category_id: Optional[int] = None,
                                  limit: int = 50,
                                  offset: int = 0) -> List[Product]:
        """获取上架中的商品（用于商城首页）"""
        conditions = [Product.status == 'active']

        if category_id:
            conditions.append(Product.category_id == category_id)

        stmt = (
            select(Product)
            .where(and_(*conditions))
            .order_by(Product.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def exists(self, product_id: int) -> bool:
        """检查商品是否存在"""
        stmt = select(Product.id).where(Product.id == product_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    # ========== 创建与更新 ==========

    async def create(self, product_data: ProductCreateSchema, seller_id: int) -> Product:
        """创建新商品"""
        # 确保卖家ID正确设置
        product_dict = product_data.model_dump()
        product_dict['seller_id'] = seller_id

        product = Product(**product_dict)
        self.session.add(product)

        await self.session.flush()
        await self.session.refresh(product, ['category', 'seller'])

        return product

    async def update(self, product_id: int, update_data: ProductUpdateSchema) -> Optional[Product]:
        """更新商品信息"""
        # 使用session.execute进行更新，避免先查询再更新
        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            return None

        stmt = (
            update(Product)
            .where(Product.id == product_id)
            .values(**update_dict)
            .returning(Product)
        )

        result = await self.session.execute(stmt)
        updated_product = result.scalar_one_or_none()

        if updated_product:
            # 重新加载关联关系
            await self.session.refresh(updated_product, ['category', 'seller'])

        return updated_product

    async def update_status(self, product_id: int, status: str) -> bool:
        """更新商品状态"""
        stmt = (
            update(Product)
            .where(Product.id == product_id)
            .values(status=status)
        )

        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def update_stock(self, product_id: int, quantity: int, reduce: bool = True) -> bool:
        """更新库存（增减）"""
        product = await self.get_by_id(product_id, include_relations=False)
        if not product:
            return False

        new_stock = product.stock - quantity if reduce else product.stock + quantity
        if new_stock < 0:
            return False

        product.stock = new_stock

        # 自动更新状态
        if new_stock == 0:
            product.status = 'out_of_stock'
        elif product.status == 'out_of_stock' and new_stock > 0:
            product.status = 'draft'  # 需要商家重新上架

        await self.session.flush()
        return True

    # ========== 删除方法 ==========

    async def delete(self, product_id: int) -> bool:
        """删除商品"""
        stmt = delete(Product).where(Product.id == product_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def delete_by_seller(self, seller_id: int, product_ids: List[int]) -> int:
        """批量删除商家的商品"""
        stmt = delete(Product).where(
            and_(
                Product.seller_id == seller_id,
                Product.id.in_(product_ids)
            )
        )
        result = await self.session.execute(stmt)
        return result.rowcount

    # ========== 统计方法 ==========

    async def count_by_seller(self, seller_id: int) -> int:
        """统计商家的商品数量"""
        stmt = select(Product.id).where(Product.seller_id == seller_id)
        result = await self.session.execute(stmt)
        return len(result.scalars().all())

    async def count_by_category(self, category_id: int) -> int:
        """统计分类下的商品数量"""
        stmt = select(Product.id).where(Product.category_id == category_id)
        result = await self.session.execute(stmt)
        return len(result.scalars().all())
