from pydantic import BaseModel, Field, ConfigDict

from typing import Optional

# base
class CategoryBase(BaseModel):
    name:str = Field(..., description="Please input category name", examples=["Beverages"])

# Create
class CategoryCreate(CategoryBase):
    pass

#Update
class CategoryUpdate(BaseModel):
    name: Optional[str] = None

# Response
class CategoryResponse(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Delete
class CategoryDelete(BaseModel):
    id: int