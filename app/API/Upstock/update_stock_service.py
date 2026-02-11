from ormModels import Menu, Update_stock, menuStatus
from app.models.Update_Stock.upstock_schema import UpstockCreate, UpstockDelete, UpstockResponse, UpstockUpdate
from app.models.Menu.menu_schema import MenuUpdate
from fastapi import HTTPException
from sqlalchemy import update

from sqlalchemy.orm import Session

# get all

def get_all_upstock(db:Session):
    return db.query(Update_stock).all()

# get by id
def get_upstock_by_id(db:Session, id:int):
    upstock = db.query(Update_stock).filter(Update_stock.id == id).first()
    if not upstock:
        raise HTTPException(status_code=404, detail="Update Stock not found")
    return upstock

# Create upstock
def create_upstock_id(db:Session, request:UpstockCreate):
    # Check menu 
    menu = db.query(Menu).filter(Menu.id == request.menu_id).with_for_update().first()
    if not menu:
        raise HTTPException(status_code=404, detail=f"Menu not found for the given menu_id :{request.menu_id}") 

    # Atomic Update for daily_portion
    db.execute(
        update(Menu)
        .where(Menu.id == request.menu_id)
        .values(daily_portion=Menu.daily_portion + request.stock_after)
    )

    # Refresh menu object from db to get latest value for status check
    db.refresh(menu)

    if menu.daily_portion > 0:
        menu.status = menuStatus.available
    
    # create log update stock menu
    new_upstock = Update_stock(**request.model_dump())

    db.add(new_upstock)
    db.commit()
    db.refresh(new_upstock)
    return new_upstock

