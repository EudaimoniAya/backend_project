from pydantic import BaseModel, Field
from datetime import datetime


class CategoryBaseSchema(BaseModel):
    """分类基础Schema"""
    name: str = Field(..., min_length=1, max_length=100, description="分类名称")


class CategoryCreateSchema(CategoryBaseSchema):
    """创建分类Schema"""
    pass


class CategoryUpdateSchema(BaseModel):
    """更新分类Schema"""
    name: str | None = Field(None, min_length=1, max_length=100)


class CategoryResponseSchema(BaseModel):
    """分类响应Schema"""
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class CategoryWithProductsSchema(CategoryResponseSchema):
    """包含商品的分类Schema"""
    from schemas.product import ProductResponseSchema
    products: list[ProductResponseSchema] = []

    class Config:
        from_attributes = True
