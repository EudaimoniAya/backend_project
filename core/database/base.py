"""
此处（`core/database/base.py`）仅负责统一定义的 ORM Base 类，它将在两处使用：
* 传统后端的`models/`定义业务数据实体
* AI应用的`core/ai/data/models`定义向量模型和AI会话模型
这两处定义的所有子类将在`core/models/__init__.py`集中导入，用作 alembic 模型迁移

注：Base.metadata需要被`core/database/engine.py`中的引擎调用，用于创建表
所以 Base 的所有子类都不应该再导入 `core/database/engine.py`内容，避免循环依赖
"""
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base类是所有ORM Model类的父类。只有继承自Base类才能够同步到数据库当中生成一张表
    否则就要通过反射，让数据库中的数据映射到类
    """
    metadata = MetaData(naming_convention={
        # ix: index，索引
        "ix": "ix_%(column_0_label)s",
        # un: unique，唯一约束
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        # ck: Check，检查约束
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        # fk: Foreign Key，外键约束
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        # pk: Primary Key，主键约束
        "pk": "pk_%(table_name)s"
    })


__all__ = ["Base"]
