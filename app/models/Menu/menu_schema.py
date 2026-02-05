from pydantic import BaseModel, Field, ConfigDict

from typing import Optional

from enum import Enum

#ENUM
class menuStatus(str, Enum):
    available = "available"   
    outofstock = "outOfStock"\
    
# base
class MenuBase(BaseModel):
    name: str = Field(..., description="Please input menu name", examples=["Nasi Goreng"])
    daily_portion: int = Field(..., description="Please input daily portion", examples=[10])
    price: int = Field(..., description="Please Input Price Menu", examples=[15000])
    status: menuStatus = Field(..., description="Current Menu Status", examples=["Pending"])
    category_id: int = Field(..., description="Category ID", examples=[1])
    description: str = Field(..., description="Input Menu Description", examples=["Fried Rice, Eggs, Shredded Chicken"])
    image: str = Field(..., description="Please input Image URL", examples=["https://i.pinimg.com/736x/8e/af/ae/8eafae4853808152081ad876648522da.jpg"])

# create
class MenuCreate(MenuBase):
    pass

# update
class MenuUpdate(BaseModel):
    name: Optional[str] = None
    daily_portion: Optional[int] = None 
    price: int = None
    status: menuStatus = None 
    category_id: int = None
    description: str = None  
    image: str = None

# Response
class MenuResponse(MenuBase):
    id:int
    model_config = ConfigDict(from_attributes=True)

# Delete
class MenuDelete(BaseModel):
    id: int


