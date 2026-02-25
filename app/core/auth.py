from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from ormModels import Users
from sqlalchemy.orm import Session
from app.core.deps import get_db
from dotenv import load_dotenv
import os
from ormModels import UserRole

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

oauth2_scheme= OAuth2PasswordBearer(tokenUrl="/auth/login")

class Token(BaseModel):
    """Response ketika login sukses"""
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    """Isi token setelah di-decode"""
    sub: Optional[str] = None   # user_id 
    username: Optional[str] = None # username
    role: Optional[str] = None  # anggota/petugas
    purpose: Optional[str] = None # purpose of token (e.g., 'access', 'reset_password')
    exp: Optional[int] = None   # expiry time
    
    
"""Membuat Access Token"""
def create_access_token(subject:str , expires_delta: Optional[timedelta] = None, extra: Optional[dict[str, Any]] = None) -> str:
    now = datetime.now(timezone.utc)
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = now + expires_delta
    
    to_encode: Dict[str, Any] = {"sub": subject, "iat": int(now.timestamp()), "exp": int(expire.timestamp()) }
    if extra:
        to_encode.update(extra)
        
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

"""Decode dan verifikasi Access Token"""
def verify_access_token(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"}
                                          )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None:
            raise credentials_exception
        
        return TokenPayload(
            sub=user_id, 
            role=role, # Bisa None jika tidak ada
            username=payload.get("username"),
            exp=payload.get("exp")
        )
    except JWTError:
        raise credentials_exception
    
    """ ================= ROLE CHECK DEPENDENCY ================= """
def require_role(*allowed_role: UserRole):
    """
    Dependency reusable untuk membatasi akses endpoint berdasarkan role.
    """
    def dependency(current_user: Users = Depends(get_current_user)):
        if current_user.role not in allowed_role:
            allowed = ', '.join([role.value for role in allowed_role])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Your role doesn't allow this action. Required role: {allowed}"
            )
        return current_user
    return dependency


""" ================= OPTIONAL HELPER ================= """
""" Mengambil user yang sedang login universal"""
def get_current_user(
    db: Session = Depends(get_db),
    token_data: TokenPayload = Depends(verify_access_token),
):
    try:
        user_id = int(token_data.sub)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject"
        )

    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user