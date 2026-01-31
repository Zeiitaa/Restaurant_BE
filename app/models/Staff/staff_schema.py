from pydantic import BaseModel, Field, ConfigDict

from typing import Optional

from enum import Enum

# ENUM YANG DIPAKE
class staffStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    resign = "resign"

class staffPosition(str, Enum):
    admin = "admin" 
    manager = "manager"
    waiters = "waiters"
    employee = "employee"

# Buat Base Model
class StaffBase(BaseModel):
    name: str = Field(..., description="Please input your name", examples=["Andhika"])
    phone_number: str = Field(..., description="Please input your phone number", examples=["08123456789"])
    address: str = Field(..., description="Please input your address", examples=["Jl. Contoh No. 01"])
    username: str = Field(..., description="Please input your username", examples=["Zeita"])
    status: staffStatus = Field(..., description="Please input your status", examples=[staffStatus.active])    
    position: staffPosition = Field(..., description="Please input your position", examples=[staffPosition.waiters])

class staffCreate(StaffBase):
    password: str = Field(..., description="Please input your password")

class staffUpdate(BaseModel):
    name: Optional[str] = None  
    username: Optional[str] = None
    password: Optional[str] = None
    status: Optional[staffStatus] = None
    positon: Optional[staffPosition] = None

class staffResponse(StaffBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class staffRegister(BaseModel):
    name: str = Field(..., description="Please input your name", examples=["Andhika"])
    phone_number: str = Field(..., description="Please input your phone number", examples=["08123456789"])
    address: str = Field(..., description="Please input your address", examples=["Jl. Contoh No. 01"])
    username: str = Field(..., description="Please input your username", examples=["Zeita"])
    password: str = Field(..., description="Please input your password")
    