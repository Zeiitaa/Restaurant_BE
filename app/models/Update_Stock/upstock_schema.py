from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

from enum import Enum

# user simple response
class UserSimpleResponse(BaseModel):
    id: int
    username: str
    model_config = ConfigDict(from_attributes=True)

# menu simple response
class MenuSimpleResponse(BaseModel):
    name: str
    category: str
    model_config = ConfigDict(from_attributes=True)

# base
class UpstockBase(BaseModel):
    menu_id: int = Field(..., description="menu_id", examples=[1])
    stock_after: int = Field(..., description="Please input Updated stock", examples=[4])
    date: datetime = Field(..., description="Date Format YYYY/MM/DD")
    users_id: int = Field(..., description="Staff Id who update the stock", examples=[2])

# create
class UpstockCreate(UpstockBase):
    pass

# update
class UpstockUpdate(BaseModel):
    menu_id: Optional[int] = None
    stock_after: Optional[int] = None
    date: Optional[datetime] = None
    users_id: Optional[int] = None
    
# response
class UpstockResponse(BaseModel):
    id: int
    menu_id: int
    stock_after: int
    date: datetime
    menu: Optional[MenuSimpleResponse] = None
    staff: Optional[UserSimpleResponse] = None
    model_config = ConfigDict(from_attributes=True)

# delete
class UpstockDelete(BaseModel):
    id: int