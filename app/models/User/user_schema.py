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
    # User fields
    username: Optional[str] = None
    password: Optional[str] = None
    status: Optional[UserStatus] = None
    role: Optional[UserRole] = None
    # UserDetail fields
    name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None

class UserDeact(BaseModel):
    status: Optional[UserStatus] = None

class UserResponse(UserBase):
    email: Optional[str] = None
    id: int
    model_config = ConfigDict(from_attributes=True)

class UserRegister(BaseModel):
    username: str = Field(..., description="Please input your username", examples=["Zeita"])
    email: str = Field(..., description="Please input your email", examples=["user@example.com"])
    password: str = Field(..., description="Please input your password")
    confirm_password: str = Field(..., description="Please confirm your password")

class ForgotPassword(BaseModel):
    email: str = Field(..., description="Please input your email", examples=["user@example.com"])

class ResetPassword(BaseModel):
    email: str = Field(..., description="Please input your email", examples=["user@example.com"])
    otp_code: str = Field(..., description="Please input the OTP code you received",  min_length=6, max_length=6)
    new_password: str = Field(..., description="Please input your new password")

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

 
