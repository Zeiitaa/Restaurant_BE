from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import getDB
from app.API.auth import auth_service
from app.core.auth import Token
from fastapi.security import OAuth2PasswordRequestForm
from app.core.auth import get_current_user, require_position
from app.models.User.user_schema import UserResponse, UserRegister
from ormModels import Users
from pydantic import BaseModel
import database

class LoginRequest(BaseModel):
    username: str
    password: str   

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
def login_endpoint(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(getDB)):
    return auth_service.login_user(db, form_data.username, form_data.password)

@router.post("/register", response_model=UserResponse)
def regist_endpoint(request:UserRegister, db:Session = Depends(database.getDB)):
    return auth_service.register_user(db, request)