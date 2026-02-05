from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

from enum import Enum

# base
class UpstockBase(BaseModel):
    menu_id: int = Field(..., description="menu_id", examples=[1])
    stock_after: int = Field(..., description="Please input Updated stock", examples=[4])
    date: datetime = Field(..., description="Date Format YYYY/MM/DD")

# create
class UpstockCreate(UpstockBase):
    pass

# update
class UpstockUpdate(BaseModel):
    menu_id: Optional[int] = None
    stock_after: Optional[int] = None
    date: Optional[datetime] = None

# response
class UpstockResponse(UpstockBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# delete
class UpstockDelete(BaseModel):
    id: int