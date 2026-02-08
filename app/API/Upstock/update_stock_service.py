from ormModels import Update_stock
from app.models.Update_Stock.upstock_schema import UpstockCreate, UpstockDelete, UpstockResponse, UpstockUpdate

from fastapi import HTTPException

from sqlalchemy.orm import Session

# get all

def get_all_upstock(db:Session):
    return db.query(Update_stock).all()

# get by id
def get_upstock_by_id(db:Session, id:int):
    upstock = db.query(Update_stock).filter(Update_stock.id == id)
    if not upstock:
        raise HTTPException(status_code=404, detail="Update Stock not found")
    return upstock

# Create upstock
# def 
