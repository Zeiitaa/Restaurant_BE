from app.models.User.user_schema import UserUpdate, UserRegister, UserResponse, UserCreate, UserDeact, UserDetailCreateBase, UserDetailUpdate, StaffDetailCreateBase, StaffDetailUpdate, StaffDetailResponse, UserandDetail
from ormModels import Users, UserRole, UserStatus, UserDetails, StaffDetails
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password

#Fungsi Tambah User
def create_user(db:Session, request:UserCreate):
    new_user = Users(
        username = request.username,
        password = hash_password(request.password),
        status = UserStatus.active,
        role = request.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# untuk isi detail user dan staff
def create_detail_user(db:Session, request:UserDetailCreateBase, user_id:int):
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

def create_detail_staff(db:Session, request:StaffDetailCreateBase, user_id:int):
    new_detail_staff = StaffDetails(
        name = request.name,
        phone_number = request.phone_number,
        address = request.address,
        users_id = user_id
    )
    db.add(new_detail_staff)
    db.commit()
    db.refresh(new_detail_staff)
    return new_detail_staff

#ambil semua data user
def get_all_user(db:Session):
    return db.query (Users).all()

def get_all_user_detailed(db: Session):
    # Melakukan JOIN antara Users dan UserDetails
    results = db.query(Users, UserDetails).join(UserDetails, Users.id == UserDetails.users_id).all()
    
    # Mapping hasil join ke schema UserandDetail
    user_list = []
    for user, detail in results:
        user_list.append(UserandDetail(
            id=user.id,
            username=user.username,
            status=user.status.value,
            role=user.role.value,
            name=detail.name,
            phone_number=detail.phone_number,
            address=detail.address
        ))
    return user_list


# ambil data user sesuai ID
def get_user(id:int, db:Session):
    # Cek apakah ID ini benar atau engga
    user = db.query(Users).filter(Users.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Can't find user")
    return user

# Update user
def update_user(id: int, request: UserUpdate, db: Session):
    # 1. Get User
    user = db.query(Users).filter(Users.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 2. Get Data
    data = request.model_dump(exclude_unset=True)
    
    # 3. Update User fields
    user_fields = ["username", "password", "status", "role"]
    for field in user_fields:
        if field in data:
            if field == "password":
                if data[field]: # Only hash if password is not empty
                    setattr(user, field, hash_password(data[field]))
            else:
                setattr(user, field, data[field])
    
    # 4. Update UserDetail fields
    detail_fields = ["name", "phone_number", "address"]
    # Check if any detail field is in the request
    if any(field in data for field in detail_fields):
        user_detail = db.query(UserDetails).filter(UserDetails.users_id == id).first()
        
        if not user_detail:
            # If creating new detail, we need to ensure all required fields are present if not found
            # However, since this is PATCH, typically we only update what's present.
            # But creating a new row requires all non-nullable columns.
            # We can check if all required fields are present in data before creating.
            missing_fields = [f for f in detail_fields if f not in data]
            if missing_fields:
                 raise HTTPException(status_code=400, detail=f"User detail not found. To create one, please provide all fields: {missing_fields}")
            
            user_detail = UserDetails(users_id=id)
            db.add(user_detail)
            
        for field in detail_fields:
            if field in data:
                setattr(user_detail, field, data[field])

    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Update failed: {str(e)}")

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


