from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from app.models.token.token_schema import TokenPayload
from dotenv import load_dotenv
import os

# untuk Login via Backend
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# CONFIG JWT
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# buat Access TOKen
def create_access_token(subject: str, expires_delta: Optional[timedelta] = None, extra: Optional[dict[str, Any]] = None) -> str :
    # Ambil Current TIme
    now = datetime.now(timezone.utc)
    # membuat expire dengan kondisi jika expire itu tidak ada
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = now + expires_delta

    # lalu masukan ke dalam token 
    to_encode: Dict[str, Any] = {"sub": subject, "iat":now, "exp":expire}
    if extra:
        to_encode.update(extra)

# decode dan verif TOken
def verify_access_token(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Can't Validate Token",
                                          headers={"WWW-Authenticate": "Bearer"}
                                          )
# decode TOKEN
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        staff_id = int = payload.get("sub")
        role: str = payload.get("role")

        # cek apakah id staff ada atau engga
        if staff_id is None or role is None:
            raise HTTPException
        return TokenPayload(**payload)
    except JWTError:
        raise credentials_exception