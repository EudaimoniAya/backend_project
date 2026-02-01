"""
此处（`models/category.py`）定义了商品的分类表，它能够避免类别信息的重复存储和便于修改的功能
其中，表 categories.id 作为商品表的外键
"""
from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.base import Base

if TYPE_CHECKING:
    from models.product import Product  # 避免循环导入
"""
TYPE_CHECKING是typing模块的特殊常量，在静态类型检查时（由mypy、pyright、IDE检查），它的值为True
在Python代码实际运行时，它的值为False。它的唯一作用仅为“骗”过静态类型检查

对于之后的单引号前向引用，SQL alchemy有自己的注册表机制，与Python的导入系统独立
在定义继承自Base的类时，SQL alchemy就已经将其注册到一个全局的类注册表中，通常由Base.metadata维护
"""

class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True,
                                    comment="分类id")
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True,
                                      comment="分类名称")

    # --- 反向关系 ---
    """
    使用单引号List['Product']，能够避免循环导入：
    product.py要从category.py导入Category类；category.py要从product.py导入Product类
    如果双方都使用实际的类名，就会出现导入错误。而使用字符串形式的"前向引用"，能够解决此问题
    它表示需要一个Product或Category的类，但是可能没有定义好，仅在真正要建立关系映射时解析为实际的类
    
    比如List['Product']语义上代表一个由Product组成的列表，但是在relationship的上下文中，
    既作为一般的类型提示，还能够根据加载策略lazy决定SQL alchemy何时以及如何获取该列表：
    若lazy='select'（默认）或lazy='joined'，那么在执行category.products时会返回一个真正的列表
    若lazy='dynamic'，它会返回一个AppendQuery对象，此时可以继续链式调用进行过滤、分页等操作。
    
    所以在定义模型关系时，对另一方模型的引用一律使用单引号字符串形式，它是SQL alchemy的标准做法
    另外，足够模型导入查找不依赖于Python的import语句，只依赖于类是否被定义并注册到同一个Base的元数据中
    """
    products: Mapped[List['Product']] = relationship()
