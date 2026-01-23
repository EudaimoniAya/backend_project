"""
此处（`core/models/__init__.py`）负责统一导入所有 Base 模型的子类，用于 alembic 模型迁移
"""
from core.database.base import Base
from core.ai.data.models.product_vector import ProductVector
