"""
此处（`core/ai/data/stores/product_vector_store.py`）定义了商品向量的存储类
实现了基本的 CRUD 操作
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from typing import List, Tuple, Dict, Any
from operations.logging import logger, log_func

from core.ai.data.models.product_vector import ProductVector


class ProductVectorStore:
    """商品向量存储"""

    @log_func
    def __init__(self, session: AsyncSession):
        self.session = session
        logger.info("商品向量存储类初始化成功！")

    # 增加操作
    @log_func
    async def create(
            self,
            product_id: int,
            title: str,
            description: str,
            embedding: List[float]
    ) -> ProductVector:
        """
        创建商品向量记录
        Args:
            product_id: 商品ID
            title: 商品标题
            description: 商品描述
            embedding: 向量数据（768维）

        Returns:
            ProductVector 实例
        """
        product_vector = ProductVector(
            product_id=product_id,
            title=title,
            description=description,
            embedding=embedding
        )
        logger.info(f"进行商品向量记录创建，当前商品为: {product_vector}")
        async with self.session.begin():
            self.session.add(product_vector)
            return product_vector

    # 查询操作
    async def get_by_id(self, vector_id: int) -> ProductVector | None:
        """
        根据 ID 获取商品向量
        Args:
            vector_id: 向量记录 ID

        Returns:
            ProductVector 实例或 None
        """
        async with self.session.begin():
            product_vector = await self.session.get(ProductVector, vector_id)
            logger.info(f"进行商品向量记录查询，当前商品为: {product_vector}")
            return product_vector

    async def get_by_product_id(self, product_id: int) -> ProductVector | None:
        """
        根据 ID 获取商品向量
        Args:
            product_id: 商品 ID

        Returns:
            ProductVector 实例或 None
        """
        async with self.session.begin():
            stmt = select(ProductVector).where(ProductVector.product_id == product_id)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()

    @log_func
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[ProductVector], int]:
        """
        获取所有商品向量（分页）
        Args:
            limit: 每页数量
            offset: 偏移量

        Returns:
            (商品向量列表，总数量)
        """
        logger.info(f"开始查询所有商品信息！")
        async with self.session.begin():
            # 获取总数
            count_stmt = select(func.count()).select_from(ProductVector)
            count_result = await self.session.execute(count_stmt)
            total = int(count_result.scalar_one())
            logger.info(f"商品总数为: {total}")

            # 获取分页数据
            data_stmt = select(ProductVector).offset(offset).limit(limit)
            data_result = await self.session.execute(data_stmt)
            vectors = list(data_result.scalars().all())

            return vectors, total

    # 向量搜索
    @log_func
    async def similarity_search(
        self,
        query_embedding: List[float],
        distance_metric: str = 'cosine',
        limit: int = 10,
        threshold: float | None = None,
    ) -> List[Tuple[ProductVector, float]]:
        """
        向量相似度搜索

        Args:
            query_embedding: 查询向量
            distance_metric: 距离度量方式，支持 `cosine` 或 `l2`，其中余弦距离 = 1 - 余弦相似度，值越小越相似
            limit: 返回数量限制
            threshold: 距离阈值（小于等于此值才返回）

        Returns:
            列表，每个元素为(商品向量, 距离值)
            注：`cosine` 或 `l2` 度量方式都是值越小越相似（0表示完全相同）
        """
        logger.info("开始进行相似度检索！")
        # 选择距离函数
        if distance_metric.lower() == "cosine":
            # 使用 func.cosine_distance 替代直接导入
            distance_func = func.cosine_distance(ProductVector.embedding, query_embedding)
        elif distance_metric.lower() == "l2":
            # 使用 func.l2_distance 替代直接导入
            distance_func = func.l2_distance(ProductVector.embedding, query_embedding)
        else:
            raise ValueError(f"不支持的距离度量: {distance_metric}")
        logger.info(f"使用的是 {distance_metric} 度量方法")
        # 构建查询
        stmt = select(
            ProductVector,
            distance_func.label("distance")
        ).order_by(distance_func).limit(limit)

        async with self.session.begin():
            # 添加阈值过滤
            if threshold is not None:
                stmt = stmt.where(distance_func <= threshold)
            result = await self.session.execute(stmt)
            return [(vector, distance) for vector, distance in result.all()]

    async def hybrid_search(
            self,
            query_embedding: List[float],
            filter_conditions: Dict[str, Any] | None = None,
            distance_metric: str = "cosine",
            limit: int = 10
    ) -> List[Tuple[ProductVector, float]]:
        """
        混合搜索：向量相似度 + 条件过滤

        Args:
            query_embedding: 查询向量
            filter_conditions: 过滤条件，如 {"title_contains": "iPhone", "category": "电子产品"}
            distance_metric: 距离度量方式
            limit: 返回数量限制

        Returns:
            列表，每个元素为(商品向量, 距离值)
        """
        logger.info("开始进行混合检索！")
        # 选择距离函数
        if distance_metric.lower() == "cosine":
            # 使用 func.cosine_distance 替代直接导入
            distance_func = func.cosine_distance(ProductVector.embedding, query_embedding)
        elif distance_metric.lower() == "l2":
            # 使用 func.l2_distance 替代直接导入
            distance_func = func.l2_distance(ProductVector.embedding, query_embedding)
        else:
            raise ValueError(f"不支持的距离度量: {distance_metric}")
        logger.info(f"使用的是 {distance_metric} 度量方法")

        # 构建基础查询
        stmt = select(
            ProductVector,
            distance_func.label("distance")
        )

        # 添加过滤条件
        if filter_conditions:
            filters = []
            for key, value in filter_conditions.items():
                if key == "title_contains" and value:
                    filters.append(ProductVector.title.ilike(f"%{value}%"))
                elif key == "product_id" and value:
                    filters.append(ProductVector.product_id == value)
                elif key == "id" and value:
                    filters.append(ProductVector.id == value)
                # 可以添加更多过滤条件

            if filters:
                stmt = stmt.where(*filters)

        # 排序和限制
        stmt = stmt.order_by(distance_func).limit(limit)

        result = await self.session.execute(stmt)
        return [(vector, distance) for vector, distance in result.all()]

    async def delete_by_id(self, id: int) -> bool:
        """
        根据ID删除商品向量
        Args:
            id: 向量记录ID

        Returns:
            是否删除成功
        """
        stmt = delete(ProductVector).where(ProductVector.id == id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def delete_by_product_id(self, product_id: int) -> bool:
        """
        根据商品ID删除商品向量
        Args:
            product_id: 商品ID

        Returns:
            是否删除成功
        """
        stmt = delete(ProductVector).where(ProductVector.product_id == product_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    # ---------- 统计 ----------

    async def count(self) -> int:
        """统计商品向量总数"""
        stmt = select(func.count()).select_from(ProductVector)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_embedding_dimensions(self) -> int | None:
        """
        获取向量维度

        Returns:
            向量维度或None（如果没有记录）
        """
        # 获取一条记录检查向量维度
        stmt = select(ProductVector).limit(1)
        result = await self.session.execute(stmt)
        vector = result.scalar_one_or_none()

        if vector and vector.embedding:
            return len(vector.embedding)
        return None
