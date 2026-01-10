from datetime import timedelta
from pathlib import Path

from pydantic import Field, field_validator
from enum import Enum
import secrets

from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings


class EnvironmentEnum(str, Enum):
    """
    应用基础配置的environment字段类型，只能有三个：
    development     表示开发环境
    staging         表示模拟生产（预发布）环境
    production      表示生产环境
    """
    DEVELOPMENT = 'development'
    STAGING = 'staging'
    PRODUCTION = 'production'


class LogSettings(BaseSettings):
    """日志相关配置组"""
    pass


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
        return (f"postgresql://{self.session_db_user}:{self.session_db_password}@"
                f"{self.session_db_host}:{self.session_db_port}/{self.session_db_name}")


class Settings(DatabaseSettings, LogSettings):
    """总配置管理类"""

    # --- 应用基础配置 ---
    project_name: str = "backendProject"
    environment: EnvironmentEnum = Field(
        default=EnvironmentEnum.PRODUCTION,
        description="运行环境（默认为development），只有development、staging、production三种。"
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
    def validate_debug_in_production(self, v: bool, info: ValidationInfo) -> bool:
        """
        确保在生产环境中 debug 模式为 False。
        :param v:
        :param info: ValidationInfo对象，通过类型为dict[str, Any]的data属性获取所有已知字段数据
        :return: 返回验证后的debug字段值
        """
        if info.data.get('environment') == 'production' and v:
            raise ValueError('DEBUG模式在生产环境中必须为 False')
        return v  # 必须返回验证后的值

    # --- Pydantic配置 ---
    model_config = {
        "env_file": Path(__file__).parent.parent.parent / ".env",
        "env_file_encoding": "utf-8",
    }
