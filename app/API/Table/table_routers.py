from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import getDB
from app.API.Table import table_service
from app.models.Table.table_schema import TableCreate, TableResponse, TableDelete, TableUpdate, TableDeleteResponse
from pydantic import BaseModel
import database
from ormModels import UserRole, Users
from app.core.auth import get_current_user, require_role

router = APIRouter(prefix="/table", tags=["table"])

# get All
@router.get("/", response_model=list[TableResponse])
def list_table(db: Session = Depends(getDB)):
    return table_service.get_all_table(db)

# get available table
@router.get("/available", response_model=list[TableResponse])
def list_available_table(db: Session = Depends(getDB)):
    return table_service.check_available_table(db)

# get table by code
@router.get("/{code}", response_model=TableResponse)
def get_table(code: int, db: Session = Depends(getDB)):
    table = table_service.get_table_by_tablecode(db, code)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return table

# create table
@router.post("/", response_model=TableResponse)
def create_table(
    request: TableCreate, 
    db: Session = Depends(getDB), 
    current_user: Users = Depends(require_role(UserRole.admin, UserRole.manager))
):
    print(f"LOG: User {current_user.username} (ID: {current_user.id}) is creating a new table with code {request.table_code}")
    return table_service.create_table(db, request)

# update table
@router.patch("/{code}", response_model=TableResponse)
def update_table(
    code: int, 
    request: TableUpdate, 
    db: Session = Depends(getDB), 
    current_user: Users = Depends(require_role(UserRole.admin, UserRole.manager))
):
    print(f"LOG: User {current_user.username} (ID: {current_user.id}) is updating table code {code}")
    return table_service.update_table(code, db, request)

# delete table
@router.delete("/{code}", response_model=TableDeleteResponse)
def delete_table(
    code: int, 
    db: Session = Depends(getDB), 
    current_user: Users = Depends(require_role(UserRole.admin))
):
    print(f"LOG: User {current_user.username} (ID: {current_user.id}) is deleting table code {code}")
    deleted_table = table_service.delete_and_return_table(code, db)
    if not deleted_table:
        raise HTTPException(status_code=404, detail="Table not found")
    return {
        "detail": "Table successfully deleted",
        "data": deleted_table
    }