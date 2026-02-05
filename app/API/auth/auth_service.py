from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ormModels import Users
from app.core.auth import create_access_token, Token
from app.core.security import verify_password, hash_password
from app.models.User.user_schema import UserRegister

def authenticate_user(db: Session, username: str, password: str) -> Users:
    """Authenticate User by username and Password."""
    user = db.query(Users).filter(Users.username == username).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect username or password"
        )
    return user


def login_user(db: Session, username: str, password: str) -> Token:
    """Login User and return access token."""
    user = authenticate_user(db, username, password)

    access_token = create_access_token(
        subject=str(user.id),
        extra={
            "username": user.username,
            "position": user.position.value
            } #ngambil position dari user (Table databse Enum)
    )

    return Token(access_token=access_token, token_type="bearer")


# Register User
def register_user(db:Session, request: UserRegister):
    new_User = Users(
        name = request.name,
        phone_number = request.phone_number,
        address = request.address,
        username = request.username,
        password = hash_password(request.password),
    )
    db.add(new_User)
    db.commit()
    db.refresh(new_User)
    return new_User