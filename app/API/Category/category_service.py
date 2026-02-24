from app.models.Category.category_schema import CategoryCreate, CategoryDelete, CategoryResponse, CategoryUpdate
from ormModels import Category
from fastapi import HTTPException
from sqlalchemy.orm import Session

# get all
def get_all_category(db:Session):
    return db.query(Category).all()

# cretae
def create_category(db:Session, request:CategoryCreate):
    existing_category = db.query(Category).filter(Category.name == request.name).first()
    if existing_category:
        raise HTTPException(status_code=400, detail="Category with this name already exists")
    
    new_category = Category(
        name = request.name
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

# get by id
def get_category_by_id(db:Session, id:int):
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

# update
def update_category(db:Session, id:int, request:CategoryUpdate):
    # check
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    for key, value in request.model_dump(exclude_unset=True).items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)
    return category

# delete
def delete_category(db:Session, id:int):
    # check
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db.delete(category)
    db.commit()
    return category

