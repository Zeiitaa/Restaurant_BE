from pydantic import BaseModel, Field, ConfigDict

from typing import Optional

from enum import Enum

# ENUM
class TableStatus(str, Enum):
    available = "available"
    booked = "booked"

# Base Model
class TableBase(BaseModel):
    table_code: int = Field(..., description="Please input table code", examples=[1])
    status: TableStatus = Field(..., description="Please input table status", examples=["available"])
    capacity: int = Field(..., description="Please input table capacity", examples=[5])

# create
class TableCreate(TableBase):
    pass

# update
class TableUpdate(BaseModel):
    table_code: Optional[int] = None
    status: Optional[str] = None
    capacity: Optional[int] = None

# Response
class TableResponse(TableBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# delete
class TableDelete(BaseModel):
    id: int

