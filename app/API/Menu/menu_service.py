from ormModels import Menu, menuStatus
from app.models.Menu.menu_schema import MenuCreate, MenuDelete, MenuResponse, MenuUpdate

from fastapi import HTTPException

from sqlalchemy.orm import Session

# get all
def get_all_menu(db:Session):
    return db.query(Menu).all()

# get menu by id
def get_menu_by_id(db:Session, id:int):
    menu = db.query(Menu).filter(Menu.id == id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    return menu

# create menu
def create_menu(db:Session, request:MenuCreate):
    # check apakah sudah ada atau blum
    existing_menu = db.query(Menu).filter(Menu.name == request.name).first()
    if existing_menu:
        raise HTTPException(status_code=400, detail="Menu with this name already exists")
    
    new_menu = Menu(
        name = request.name,
        daily_portion = request.daily_portion,
        price = request.price,
        status = request.status,
        category_id =  request.category_id,
        description = request.description,
        image = request.image,
    )

    db.add(new_menu)
    db.commit()
    db.refresh(new_menu)
    return new_menu

# update
def update_menu(db:Session, request:MenuUpdate, id:int):
    # check id
    menu = get_menu_by_id(db, id)
    
    # check jika ada menu lain dengan nama yang sama
    if request.name:
        check_name = db.query(Menu).filter(Menu.name == request.name, Menu.id != id).first()
        if check_name:
            raise HTTPException(status_code=400, detail="Another menu with this name already exists")
    
    # data yang ingin di ubah
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(menu, key, value)

    db.commit()
    db.refresh(menu)
    return menu

def delete_menu(db:Session, id:int):    
    menu = get_menu_by_id(db, id)
    
    # Ganti status jadi outofstock (Soft Delete)
    menu.status = menuStatus.outofstock
    
    db.commit()
    db.refresh(menu)
    return menu
