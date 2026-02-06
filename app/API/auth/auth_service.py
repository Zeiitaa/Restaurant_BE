from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ormModels import Users, UserDetails, UserRole, UserStatus
from app.core.auth import create_access_token, Token
from app.core.security import verify_password, hash_password
from app.models.User.user_schema import UserRegister, UserDetailCreateBase

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
            "role": user.role.value
            } #ngambil role dari user (Table databse Enum)
    )

    return Token(access_token=access_token, token_type="bearer")


# Register User
def register_user(db:Session, request: UserRegister):
    # Cek apakah username sudah ada
    existing_user = db.query(Users).filter(Users.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # cek apakah password sama dengan confirm password
    if request.password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Password and Confirm Password do not match")
    
    # buat data user baru
    new_User = Users(
        username = request.username,
        password = hash_password(request.password),
        status = UserStatus.active,
        role = UserRole.customer
    )
    db.add(new_User)
    db.commit()
    db.refresh(new_User)
    return new_User

def register_detail_user(db:Session, request:UserDetailCreateBase, user_id:int):
    new_detail_user = UserDetails(
        name = request.name,
        phone_number = request.phone_number,
        address = request.address,
        users_id = user_id
    )
    db.add(new_detail_user)
    db.commit()
    db.refresh(new_detail_user)
    return new_detail_user
