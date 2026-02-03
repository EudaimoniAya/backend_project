from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class ProductBaseSchema(BaseModel):
    """商品基础Schema，用于创建和更新"""
    title: str = Field(..., min_length=1, max_length=200, description="商品标题")
    description: str = Field(..., min_length=1, description="商品描述")
    category_id: int = Field(..., gt=0, description="分类ID")
    price: int = Field(..., gt=0, description="价格（单位：分）")
    stock: int = Field(..., ge=0, description="库存数量")

    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v < 100:  # 假设最小价格为1元（100分）
            raise ValueError('价格不能低于1元')
        return v


class ProductCreateSchema(ProductBaseSchema):
    """创建商品Schema"""
    # 商家ID将从当前登录用户中获取，不需要前端传递
    pass


class ProductUpdateSchema(BaseModel):
    """更新商品Schema（部分更新）"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    category_id: Optional[int] = Field(None, gt=0)
    price: Optional[int] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    status: Optional[str] = Field(None, pattern='^(draft|active|inactive|out_of_stock)$')


class ProductResponseSchema(BaseModel):
    """商品响应Schema（用于API返回）"""
    id: int
    title: str
    description: str
    category_id: int
    price: int
    stock: int
    status: str
    seller_id: int
    created_at: datetime
    updated_at: datetime

    # 包含关联数据
    class Config:
        from_attributes = True  # Pydantic V2，替代原来的orm_mode=True


class ProductWithRelationsSchema(ProductResponseSchema):
    """包含关联数据的商品Schema"""
    from schemas.category import CategoryResponseSchema
    from schemas.user import UserResponseSchema

    category: Optional[CategoryResponseSchema] = None
    seller: Optional[UserResponseSchema] = None

    class Config:
        from_attributes = True