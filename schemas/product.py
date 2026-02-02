from pydantic import BaseModel, Field


class ProductBaseSchema(BaseModel):
    """商品基础Schema，用于创建和更新"""
    title: str = Field(..., min_length=1, max_length=200, description="商品标题")
    description: str = Field(..., min_length=1, description="商品描述")
    category_id: int = Field(..., gt=0, description="分类ID")
    price: int = Field(..., gt=0, description="价格（单位：分）")
    stock: int = Field(..., ge=0, description="库存数量")