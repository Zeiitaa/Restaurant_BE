import ormModels, database
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.token.token_schema import TokenPayload
from security.auth import verify_access_token

# config untuk hash passwrod
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# fungsi Hashing
def hash_password(password:str) -> str:
    return pwd_context.hash(password)

# fungsi Verif password
def verify_password(plain_password:str, hashed_password:str) -> str:
    return pwd_context.verify(plain_password, hashed_password)

# fungsi mendapatkan staff saat ini
def get_current_staff(db:Session = Depends(database.getDB), token:TokenPayload = Depends(verify_access_token)):
    staff = db.query (ormModels.Staff).filter(ormModels.Staff.id == token.sub).first()
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Can't find User"
        )
    return staff

# fungsi yang membutuhkan role, akan di cek menggunakan fungsi ini
def require_role(role:str):
    # ambil dulu staff saat ini
    def role_checker(current_staff: ormModels.Staff = Depends(get_current_staff)):
        if current_staff.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=f"required role: {role}"
            )
        return current_staff
    return role_checker