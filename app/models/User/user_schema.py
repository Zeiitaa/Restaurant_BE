from pydantic import BaseModel, Field, ConfigDict

from typing import Optional

from enum import Enum

# ENUM YANG DIPAKE
class UserStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    resign = "resign"

class UserRole(str, Enum):
    admin = "admin" 
    manager = "manager"
    waiters = "waiters"
    employee = "employee"
    customer = "customer"

# Buat Base Model
class UserBase(BaseModel):
    username: str = Field(..., description="Please input your username", examples=["Zeita"])
    status: UserStatus = Field(..., description="Please input your status", examples=[UserStatus.active])    
    role: UserRole = Field(..., description="Please input your role", examples=[UserRole.waiters])

class UserCreate(UserBase):
    password: str = Field(..., description="Please input your password")

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    status: Optional[UserStatus] = None
    role: Optional[UserRole] = None

class UserDeact(BaseModel):
    status: Optional[UserStatus] = None

class UserResponse(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class UserRegister(BaseModel):
    username: str = Field(..., description="Please input your username", examples=["Zeita"])
    password: str = Field(..., description="Please input your password")
    confirm_password: str = Field(..., description="Please confirm your password")

class UserDetailCreateBase(BaseModel):
    name: str = Field(..., description="Please input your name", examples=["Andhika"])
    phone_number: str = Field(..., description="Please input your phone number", examples=["08123456789"])
    address: str = Field(..., description="Please input your address", examples=["Jl. Contoh No. 01"])

class UserDetailResponse(UserDetailCreateBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class UserDetailUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None

class StaffDetailCreateBase(BaseModel):
    name: str = Field(..., description="Please input your name", examples=["Andhika"])
    phone_number: str = Field(..., description="Please input your phone number", examples=["08123456789"])
    address: str = Field(..., description="Please input your address", examples=["Jl. Contoh No. 01"])

class StaffDetailResponse(StaffDetailCreateBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class StaffDetailUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None

class UserandDetail(BaseModel):
    id: int
    username: str
    status: UserStatus
    role: UserRole
    name: str
    phone_number: str
    address: str
    model_config = ConfigDict(from_attributes=True)

 
