from pydantic import BaseModel, EmailStr, constr
from models.user import UserRole


class UserCreateSchema(BaseModel):
    """
    注册成功时，将规范的RegisterIn数据提取必要的一部分作为创建用户数据，和ORM模型对接的Schema
    具体的对接就是通过BaseModel子类继承的model_dump()，将这个字典通过**kwargs传给ORM模型
    """
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=8,  max_length=100)
    role: UserRole = UserRole.BUYER  # 默认是买家

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "securepassword123",
                "role": "buyer"
            }
        }
    }
