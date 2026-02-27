from ormModels import Menu, menuStatus
from app.models.Menu.menu_schema import MenuCreate, MenuDelete, MenuResponse, MenuUpdate
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException

# get all
def get_all_menu(db:Session):
    return db.query(Menu).options(joinedload(Menu.category)).all()

def get_available_menus(db:Session):
    available_menus = db.query(Menu).options(joinedload(Menu.category)).filter(Menu.status != menuStatus.outofstock).all()
    return available_menus

# get menu by id
def get_menu_by_id(db:Session, id:int, lock:bool = False):
    if lock:
        # Separate query for locking without eager loading to avoid join issues with FOR UPDATE
        menu = db.query(Menu).filter(Menu.id == id).with_for_update().first()
    else:
        # Standard query with eager loading for read operations
        menu = db.query(Menu).options(joinedload(Menu.category)).filter(Menu.id == id).first()
        
    if not menu:
        raise HTTPException(status_code=404, detail=f"Menu with id {id} not found")
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
    menu.daily_portion = 0  # Set daily portion to 0 to reflect out of stock
    db.commit()
    db.refresh(menu)
    return menu
