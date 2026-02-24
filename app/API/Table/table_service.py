from ormModels import Table
from app.models.Table.table_schema import TableCreate, TableDelete, TableResponse, TableUpdate, TableStatus

from fastapi import HTTPException

from sqlalchemy.orm import Session

# get all
def get_all_table(db:Session):
    return db.query(Table).all()

# get available
def get_available_table(db:Session):
    available_table = db.query(Table).filter(Table.status == TableStatus.available).all()
    return available_table

# check available
def check_available_table(db:Session):
    available = get_available_table(db)
    if not available:
        return []
    return available

# get table by kode
def get_table_by_tablecode(db:Session, code: int):
    return db.query(Table).filter(Table.table_code == code).first()

# fungsi tambah meja
def create_table(db:Session, request:TableCreate):
    # check apakah sudah ada meja? (Check BEFORE adding)
    existing_table = db.query(Table).filter(Table.table_code == request.table_code).first()
    if existing_table:
        raise HTTPException(status_code=400, detail="Table with this code already exists")

    new_table = Table(
        table_code = request.table_code,
        status = TableStatus.available,
        capacity = request.capacity
    )
    db.add(new_table)
    db.commit()
    db.refresh(new_table)
    return new_table

# fungsi update meja
def update_table(code:int, db:Session, request:TableUpdate):
    # check
    table = get_table_by_tablecode(db, code)
    if not table:
        raise HTTPException(status_code=404, detail="Can't find table")

    # data yang ingin di ubah
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(table, key, value)

    db.commit()
    db.refresh(table)
    return table

def delete_and_return_table(code:int, db:Session):
    # check
    table = get_table_by_tablecode(db, code)
    if not table:
        return None

    db.delete(table)
    db.commit()
    return table