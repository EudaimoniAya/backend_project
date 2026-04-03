"""
这里将存放应用级的单例 (engine)。
它是配置（settings）到具体数据库驱动之间的桥梁，在应用启动时初始化一次。
"""
from sqlalchemy.ext.asyncio import create_async_engine
from operations.settings import settings


# 1. 创建引擎
engine = create_async_engine(
    settings.session_database_url,
    # 将输出所有执行SQL的日志（默认是关闭的）
    echo=True,
    # 连接池大小（默认是5个）
    pool_size=10,
    # 允许连接池的最大的连接数（默认是10个）
    max_overflow=20,
    # 获得连接超时时间（默认为30s）
    pool_timeout=10,
    # 连接回收时间（默认是-1，代表永不回收）
    pool_recycle=3600,
    # 连接前是否预检查（默认为False）
    pool_pre_ping=True,
)

"""
当 Python 导入一个模块时，会先检查 sys.modules 中是否已有该模块，
如果有则直接返回已存在的模块对象。如果不存在，则执行模块代码，创建
模块对象，并存入 sys.modules，随后再次导入时直接复用。

因此，在模块顶层定义的变量（例如 _instance = MyClass()）在整个解
释器生命周期中只被初始化一次，所有导入该模块的地方访问的都是同一个
对象。这里的 engine 是一个应用级单例（也叫模块级单例或import单例）
"""