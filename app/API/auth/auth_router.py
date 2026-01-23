from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.API.auth import auth_service
from app.core.auth import Token
from fastapi.security import OAuth2PasswordRequestForm
from app.core.auth import get_current_staff, require_role
from app.models.Staff.staff_schema import staffResponse 
from ormModels import Staff
from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str   

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
def login_endpoint(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return auth_service.login_staff(db, form_data.username, form_data.password)

@router.get("/profile", response_model=staffResponse)
def get_profile(current_user: Staff = Depends(get_current_staff)):
    return current_user
