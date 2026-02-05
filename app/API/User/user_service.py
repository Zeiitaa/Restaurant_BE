from app.models.User.user_schema import UserUpdate, UserRegister, UserResponse, UserCreate
from ormModels import Users, UserRole, UserStatus
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password

#Fungsi Tambah User
def create_user(db:Session, request:UserCreate ):
    new_user = Users(
        name = request.name,
        phone_number = request.phone_number,
        address = request.address,
        username = request.username,
        password = hash_password(request.password),
        status = request.status,
        position = request.position
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

#ambil semua data user
def get_all_user(db:Session):
    return db.query (Users).all()

# ambil data user sesuai ID
def get_user(id:int, db:Session):
    # Cek apakah ID ini benar atau engga
    user = db.query(user).filter(Users.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Can't find user")
    return user

# Update user
def update_user(id:int, request:UserUpdate, db:Session):
    # check dulu
    user = db.query(Users).filter(Users.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Can't find user")
    
    # data yang ingin di ubah
    data = request.model_dump(exclude_unset=True)

    # jika di dalam data juga terdapat password baru, itu perlu di hash lagi
    if "password" in data and ["password"] is not None:
        data["password"] = hash_password[data["password"]]

    # deteksi apa aja data yang diubah
    for key, value in data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user

# deactivate user (soft delete)
def deactivate_user(id: int, request:UserUpdate, db:Session):
    # check ID
    user = db.query(Users).filter(Users.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Can't find user")
    
    if user.status == "resign":
        raise HTTPException(status_code=400, detail="user is already resigned")
    
    user.status = UserStatus.resign
    db.commit()
    db.refresh(user)
    return user


