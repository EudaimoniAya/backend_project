"""
此处（`core/models/pg_models.py`）负责统一导入所有 pg 数据库 Base 模型的子类，用于 alembic 模型迁移
"""
from core.database.base import Base
from core.ai.data.models.product_vector import ProductVector
