from ormModels import Menu, menuStatus
from app.models.Menu.menu_schema import MenuCreate, MenuDelete, MenuResponse, MenuUpdate
from sqlalchemy import select
from fastapi import HTTPException

from sqlalchemy.orm import Session

# get all
def get_all_menu(db:Session):
    return db.query(Menu).all()

def get_available_menus(db:Session):
    available_menus = db.query(Menu).filter(Menu.status != menuStatus.outofstock).all()
    return available_menus

# get menu by id
def get_menu_by_id(db:Session, id:int, lock:bool = False):
    query = db.query(Menu).filter(Menu.id == id)
    if lock:
        query = query.with_for_update()
    menu = query.first()
    if not menu:
        raise HTTPException(status_code=404, detail=f"Menu with id{id} not found")
    return menu

# create menu
def create_menu(db:Session, request:MenuCreate):
    # check apakah sudah ada atau blum
    existing_menu = db.query(Menu).filter(Menu.name == request.name).first()
    if existing_menu:
        raise HTTPException(status_code=400, detail="Menu with this name already exists")
    
    new_menu = Menu(**request.model_dump())

    db.add(new_menu)
    db.commit()
    db.refresh(new_menu)
    return new_menu

# update
def update_menu(db:Session, request:MenuUpdate, id:int):
    # Lock the row to prevent lost updates
    menu = get_menu_by_id(db, id, lock=True)
    
    # check jika ada menu lain dengan nama yang sama
    if request.name and request.name !=menu.name:
        query = select(Menu).where(Menu.name == request.name, Menu.id != id)
        existing_menu = db.execute(query).scalars().first()
        if existing_menu:
            raise HTTPException(status_code=400, detail="Another menu with this name already exists")
    
    # data yang ingin di ubah
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(menu, key, value)

    db.commit()
    db.refresh(menu)
    return menu

def delete_menu(db:Session, id:int):    
    # Lock the row
    menu = get_menu_by_id(db, id, lock=True)
    
    # Ganti status jadi outofstock (Soft Delete)
    if menu.status == menuStatus.outofstock:
        raise HTTPException(status_code=400, detail="Menu is already out of stock")
    
    menu.status = menuStatus.outofstock
    
    db.commit()
    db.refresh(menu)
    return menu
