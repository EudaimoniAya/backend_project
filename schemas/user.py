from pydantic import BaseModel, EmailStr, constr
from models.user import UserRole


class UserCreateSchema(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=8)
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
