from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from ormModels import Staff
from sqlalchemy.orm import Session
from app.core.deps import get_db
from dotenv import load_dotenv
import os
from ormModels import staffPosition

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
    sub: Optional[str] = None   # staff_id 
    username: Optional[str] = None # username
    position: Optional[str] = None  # anggota/petugas
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
        staff_id: str = payload.get("sub")
        position: str = payload.get("position")
        if staff_id is None or position is None:
            raise credentials_exception
        
        return TokenPayload(sub=staff_id, position=position, exp=payload.get("exp"))
    except JWTError:
        raise credentials_exception
    
    """ ================= POSITION CHECK DEPENDENCY ================= """
def require_position(*allowed_position: staffPosition):
    """
    Dependency reusable untuk membatasi akses endpoint berdasarkan Position.
    """
    def dependency(current_user: Staff = Depends(get_current_staff)):
        if current_user.position not in allowed_position:
            allowed = ', '.join([position.value for position in allowed_position])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Your position doesn't allow this action. Required position: {allowed}"
            )
        return current_user
    return dependency


""" ================= OPTIONAL HELPER ================= """
""" Mengambil user yang sedang login universal"""
def get_current_staff(
    db: Session = Depends(get_db),
    token_data: TokenPayload = Depends(verify_access_token),
):
    try:
        staff_id = int(token_data.sub)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject"
        )

    user = db.query(Staff).filter(Staff.id == staff_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user