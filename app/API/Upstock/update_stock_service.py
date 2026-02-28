from ormModels import Menu, Update_stock, menuStatus, Users, Category
from app.models.Update_Stock.upstock_schema import UpstockCreate, UpstockDelete, UpstockResponse, UpstockUpdate, UserSimpleResponse, MenuSimpleResponse
from app.models.Menu.menu_schema import MenuUpdate
from fastapi import HTTPException
from sqlalchemy import update

from sqlalchemy.orm import Session

# get all

def get_all_upstock(db:Session):
    upstocks = db.query(Update_stock).all()
    results = []
    for u in upstocks:
        # Get staff info
        staff_info = db.query(Users).filter(Users.id == u.users_id).first()
        
        # Get menu and category info
        menu_info = db.query(Menu).filter(Menu.id == u.menu_id).first()
        category_name = "-"
        if menu_info and menu_info.category:
            category_name = menu_info.category.name

        results.append(UpstockResponse(
            id=u.id,
            menu_id=u.menu_id,
            stock_after=u.stock_after,
            date=u.date,
            menu=MenuSimpleResponse(name=menu_info.name, category=category_name) if menu_info else None,
            staff=UserSimpleResponse(id=staff_info.id, username=staff_info.username) if staff_info else None
        ))
    return results

# get by id
def get_upstock_by_id(db:Session, id:int):
    u = db.query(Update_stock).filter(Update_stock.id == id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Update Stock not found")
    
    staff_info = db.query(Users).filter(Users.id == u.users_id).first()
    
    # Get menu info
    menu_info = db.query(Menu).filter(Menu.id == u.menu_id).first()
    category_name = "-"
    if menu_info and menu_info.category:
        category_name = menu_info.category.name

    return UpstockResponse(
        id=u.id,
        menu_id=u.menu_id,
        stock_after=u.stock_after,
        date=u.date,
        menu=MenuSimpleResponse(name=menu_info.name, category=category_name) if menu_info else None,
        staff=UserSimpleResponse(id=staff_info.id, username=staff_info.username) if staff_info else None
    )

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
    
    # Get staff info for response
    staff_info = db.query(Users).filter(Users.id == new_upstock.users_id).first()
    
    # Get category name
    category_name = "-"
    if menu.category:
        category_name = menu.category.name

    return UpstockResponse(
        id=new_upstock.id,
        menu_id=new_upstock.menu_id,
        stock_after=new_upstock.stock_after,
        date=new_upstock.date,
        menu=MenuSimpleResponse(name=menu.name, category=category_name),
        staff=UserSimpleResponse(id=staff_info.id, username=staff_info.username) if staff_info else None
    )

