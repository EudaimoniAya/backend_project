from datetime import timedelta
from pathlib import Path
from typing import Dict

from pydantic import Field, field_validator
from enum import Enum
import secrets

from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings


class EnvironmentEnum(str, Enum):
    """
    应用基础配置的environment字段类型，只能有四个：
    development     表示开发环境
    test            表示测试环境
    staging         表示模拟生产（预发布）环境
    production      表示生产环境
    """
    DEVELOPMENT = 'development'
    TEST = 'test'
    STAGING = 'staging'
    PRODUCTION = 'production'


class ModelPricing(BaseSettings):
    """单个模型的定价配置"""
    input_price_per_1k: float = Field(..., description="每1000个输入token的价格（美元）")
    output_price_per_1k: float = Field(..., description="每1000个输出token的价格（美元）")
    # 如果是多模态，考虑其他信息输入方式


class AIServerSettings(BaseSettings):
    """AI相关配置组"""
    # --- API密钥配置 ---
    deepseek_api_key: str = Field(...)
    deepseek_api_base: str | None = Field("https://api.deepseek.com")

    # --- 模型计费配置 ---
    model_pricing: Dict[str, ModelPricing] = Field(
        default_factory=lambda: {
            "deepseek-chat": ModelPricing(
                input_price_per_1k=0.00055,
                output_price_per_1k=0.0017,
            ),
            "deepseek-reasoner": ModelPricing(
                input_price_per_1k=0.00055,
                output_price_per_1k=0.0017,
            ),
            # 之后可在此扩展更多模型
        },
        description="各模型的Token计价标准"
    )

    # 获取价格的辅助方法
    def get_pricing(self, model_name: str) -> ModelPricing:
        """安全地获取模型定价，如果未配置则返回一个默认值"""
        return self.model_pricing.get(
            model_name,
            ModelPricing(
                input_price_per_1k=0.0025,  # 设置较高默认值，确保成本被注意到
                output_price_per_1k=0.01,
            )
        )


class DatabaseSettings(BaseSettings):
    """数据库相关配置组"""

    # --- 主数据库（MySQL，用于用户、核心业务） ---
    main_db_host: str = Field("localhost")
    main_db_port: int = Field(3306)
    main_db_user: str = Field("root")
    main_db_password: str = Field(...)
    main_db_name: str = Field(...)

    @property
    def main_database_url(self) -> str:
        """动态构建MySQL异步连接字符串，未配置则返回None"""
        return (f"mysql+aiomysql://{self.main_db_user}:{self.main_db_password}@"
                f"{self.main_db_host}:{self.main_db_port}/{self.main_db_name}?"
                f"charset=utf8mb4")

    @property
    def main_database_sync_url(self) -> str:
        """动态构建MySQL同步连接字符串（用于Alembic迁移），未配置则返回None"""
        return (f"mysql+pymysql://{self.main_db_user}:{self.main_db_password}@"
                f"{self.main_db_host}:{self.main_db_port}/{self.main_db_name}?"
                f"charset=utf8mb4")

    # --- 会话数据库（postgresql，存储agent上下文） ---
    session_db_host: str = Field("localhost")
    session_db_port: int = Field(5432)
    session_db_user: str = Field("postgres")
    session_db_password: str = Field(...)
    session_db_name: str = Field(...)

    @property
    def session_database_url(self) -> str | None:
        """动态构建postgresql异步连接字符串，未配置则返回None"""
        if not all([self.session_db_host, self.session_db_password, self.session_db_name]):
            return None
        return (f"postgresql+asyncpg://{self.session_db_user}:{self.session_db_password}@"
                f"{self.session_db_host}:{self.session_db_port}/{self.session_db_name}")

    @property
    def session_database_sync_url(self) -> str | None:
        """动态构建postgresql同步连接字符串（用于Alembic迁移），未配置则返回None"""
        if not all([self.session_db_host, self.session_db_password, self.session_db_name]):
            return None
        return (f"postgresql+psycopg2://{self.session_db_user}:{self.session_db_password}@"
                f"{self.session_db_host}:{self.session_db_port}/{self.session_db_name}")

    # --- 商品向量数据库（postgresql，存储商品向量） ---
    product_vector_db_host: str = Field("localhost")
    product_vector_db_port: int = Field(55432)
    product_vector_db_user: str = Field("postgres")
    product_vector_db_password: str = Field(...)
    product_vector_db_name: str = Field(...)

    @property
    def product_vector_database_url(self) -> str | None:
        """动态构建postgresql异步连接字符串，未配置则返回None"""
        if not all([self.product_vector_db_host, self.product_vector_db_password, self.product_vector_db_name]):
            return None
        return (f"postgresql+asyncpg://{self.product_vector_db_user}:{self.product_vector_db_password}@"
                f"{self.product_vector_db_host}:{self.product_vector_db_port}/{self.product_vector_db_name}")

    @property
    def product_vector_database_sync_url(self) -> str | None:
        """动态构建postgresql同步连接字符串（用于Alembic迁移），未配置则返回None"""
        if not all([self.product_vector_db_host, self.product_vector_db_password, self.product_vector_db_name]):
            return None
        return (f"postgresql+psycopg2://{self.product_vector_db_user}:{self.product_vector_db_password}@"
                f"{self.product_vector_db_host}:{self.product_vector_db_port}/{self.product_vector_db_name}")


class Settings(DatabaseSettings, AIServerSettings):
    """总配置管理类"""

    # --- 应用基础配置 ---
    project_name: str = "backendProject"
    environment: EnvironmentEnum = Field(
        default=EnvironmentEnum.DEVELOPMENT,
        description="运行环境（默认为development），只有development、test、staging、production四种。"
    )
    debug: bool = Field(default=True, description="调试模式开关，为True时会打印详细信息，生产环境应关闭。")
    api_v1_str: str = Field(default="/api/v1", description="API路由前缀，用于版本管理")

    # --- 安全配置 ---
    jwt_secret_key: str = Field(default=secrets.token_urlsafe(32),
                                description="鉴权使用的JWT密钥，每次服务器重启都不一样，作为服务器的签名")
    # 使用双token机制进行JWT鉴权
    jwt_access_token_expires: timedelta = Field(timedelta(days=7), description="短期令牌过期时间")
    jwt_refresh_token_expires: timedelta = Field(timedelta(days=30), description="长期令牌过期时间")

    # --- LangSmith追踪 ---
    langsmith_tracing: bool = Field(False)
    langsmith_api_key: str | None = Field(None)
    langsmith_project: str | None = Field(None)

    # --- 验证器 ---
    @field_validator('debug', mode='after')
    def validate_debug_in_production(cls, v: bool, info: ValidationInfo) -> bool:
        """
        确保在生产环境中 debug 模式为 False。
        :param v:
        :param info: ValidationInfo对象，通过类型为dict[str, Any]的data属性获取所有已知字段数据
        :return: 返回验证后的debug字段值
        """
        if info.data.get('environment') == 'production' and v:
            raise ValueError('DEBUG模式在生产环境中必须为 False')
        return v  # 必须返回验证后的值

    # --- Pydantic配置 （初期） ---
    model_config = {
        "env_file": Path(__file__).parent.parent.parent / ".env",
        "env_file_encoding": "utf-8",
    }

    # model_config = SettingsConfigDict(
    #     # 重要：env_file 现在可以是一个列表，按照顺序加载，后面的覆盖前面的
    #     env_file=[
    #         # 1. 首先加载项目根目录的通用 .env 文件（基础默认值）
    #         Path(__file__).parent.parent.parent / ".env",
    #         # 2. 然后根据 ENVIRONMENT 环境变量的值，加载环境特定文件
    #     ],
    #     env_file_encoding="utf-8",
    #     # 允许通过 _env_file 属性在运行时动态地添加一个更高优先级的配置文件
    #     extra="allow",
    # )

# # --- 新增：用于动态添加测试配置文件的内部属性 ---
#     _test_env_file: Path | None = None
#
#     @classmethod
#     def set_test_env_file(cls, file_path: Path):
#         """
#         专门供测试夹具（pytest）调用的方法。
#         用于在运行测试前，设置一个最高优先级的 ..env.test 配置文件。
#         """
#         cls._test_env_file = file_path
#
#     @property
#     def _env_file(self) -> Path | None:
#         """
#         动态决定要加载的‘环境特定’配置文件。
#         Pydantic-Settings 会读取此属性。
#         """
#         # 优先级 1：如果设置了测试文件，则使用它（测试环境最高）
#         if self._test_env_file and self._test_env_file.exists():
#             return self._test_env_file
#         # 优先级 2：根据当前的 `environment` 字段值加载对应环境文件
#         # 注意：这里的 `self.environment` 可能来自已加载的较低优先级配置（如.env）
#         # 但我们通过 `env_file` 列表的顺序确保了后加载的会覆盖先加载的。
#         env_specific_file = Path(__file__).parent.parent.parent / f".env.{self.environment.value}"
#         if env_specific_file.exists():
#             return env_specific_file
#         # 优先级 3：没有特定环境文件
#         return None
#
#     @classmethod
#     def reload_for_test(cls):
#         """
#         强制重新加载配置（打破单例在测试中的僵化）。
#         在企业级CI中，每次测试都是全新的进程，此问题不明显。
#         在本地重复运行测试时，此方法非常有用。
#         """
#         # 清除可能存在的实例缓存，促使创建新实例
#         # 注意：这要求你的应用代码通过函数调用获取settings，而不是导入一个全局实例
#         # 例如：使用 `get_settings()` 函数而不是直接导入 `settings` 对象
#         if hasattr(cls, "_instance"):
#             delattr(cls, "_instance")
