from pydantic import BaseModel, Field, ConfigDict

from typing import Optional

from enum import Enum

# ENUM YANG DIPAKE
class staffStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    resign = "resign"

class staffRole(str, Enum):
    admin = "admin"
    manager = "manager"
    waiters = "waiters"

# Buat Base Model
class StaffBase(BaseModel):
    name: str = Field(..., description="Please input your name", examples=["Andhika"])
    username: str = Field(..., description="Please input your username", examples=["Zeita"])
    status: staffStatus = Field(..., description="Please input your status", examples=[staffStatus.active])    
    role: staffRole = Field(..., description="Please input your role", examples=[staffRole.waiters])

class staffCreate(StaffBase):
    password: str = Field(..., description="Please input your password")

class staffUpdate(BaseModel):
    name: Optional[str] = None  
    username: Optional[str] = None
    password: Optional[str] = None
    status: Optional[staffStatus] = None
    role: Optional[staffRole] = None

class staffResponse(StaffBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class staffRegister(BaseModel):
    name: str = Field(..., description="Please input your name", examples=["Andhika"])
    username: str = Field(..., description="Please input your username", examples=["Zeita"])
    password: str = Field(..., description="Please input your password")
    