from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ormModels import Staff
from app.core.auth import create_access_token, Token
from app.core.security import verify_password

def authenticate_staff(db: Session, username: str, password: str) -> Staff:
    """Authenticate User by username and Password."""
    user = db.query(Staff).filter(Staff.username == username).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect username or password"
        )
    return user


def login_staff(db: Session, username: str, password: str) -> Token:
    """Login User and return access token."""
    staff = authenticate_staff(db, username, password)

    access_token = create_access_token(
        subject=str(staff.id),
        extra={
            "username": staff.username,
            "position": staff.position.value
            } #ngambil position dari user (Table databse Enum)
    )

    return Token(access_token=access_token, token_type="bearer")