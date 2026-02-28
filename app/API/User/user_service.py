from app.models.User.user_schema import UserDetailResponse, UserUpdate, UserRegister, UserResponse, UserCreate, UserDeact, UserDetailCreateBase, UserDetailUpdate, StaffDetailCreateBase, StaffDetailUpdate, StaffDetailResponse, UserandDetail
from ormModels import Users, UserRole, UserStatus, UserDetails, StaffDetails
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password

#Fungsi Tambah User
def create_user(db:Session, request:UserCreate):
    new_user = Users(
        username = request.username,
        password = hash_password(request.password),
        email = request.email,
        status = UserStatus.active,
        role = request.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# untuk isi detail user dan staff (otomatis mendeteksi role)
def create_detail_user(db: Session, request: UserDetailCreateBase, user_id: int):
    # Cari usernya dulu untuk cek rolenya
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Debugging: Print role untuk memastikan logika benar
    print(f"DEBUG: User {user.username} has role {user.role} (type: {type(user.role)})")
    
    # List role yang masuk ke StaffDetails
    staff_roles = [UserRole.manager, UserRole.waiters, UserRole.employee]
    
    # Pastikan perbandingan enum benar (menggunakan .value jika perlu, tapi SQLAlchemy Enum biasanya oke langsung)
    is_staff = user.role in staff_roles
    
    if is_staff:
        new_detail = StaffDetails(
            name=request.name,
            phone_number=request.phone_number,
            address=request.address,
            users_id=user_id
        )
        print("DEBUG: Inserting into StaffDetails")
    else:
        new_detail = UserDetails(
            name=request.name,
            phone_number=request.phone_number,
            address=request.address,
            users_id=user_id
        )
        print("DEBUG: Inserting into UserDetails")
        
    db.add(new_detail)
    db.commit()
    db.refresh(new_detail)
    return new_detail

#ambil semua data user
def get_all_user(db:Session):
    # Hanya ambil yang statusnya active atau inactive
    return db.query(Users).filter(Users.status.in_([UserStatus.active, UserStatus.inactive])).all()

def get_all_user_detailed(db: Session):
    # Melakukan JOIN antara Users dan UserDetails (dan StaffDetails sebagai fallback)
    results = db.query(Users, StaffDetails, UserDetails)\
        .outerjoin(StaffDetails, Users.id == StaffDetails.users_id)\
        .outerjoin(UserDetails, Users.id == UserDetails.users_id)\
        .filter(Users.status.in_([UserStatus.active, UserStatus.inactive])).all()
    
    # Mapping hasil ke schema UserandDetail
    user_list = []
    for user, s_detail, u_detail in results:
        detail = s_detail if s_detail else u_detail
        user_list.append(UserandDetail(
            id=user.id,
            username=user.username,
            status=user.status.value,
            role=user.role.value,
            name=detail.name if detail else "-",
            phone_number=detail.phone_number if detail else "-",
            address=detail.address if detail else "-"
        ))
    return user_list

# ambil data user sesuai ID (Support join ke tabel manapun)
def get_user(id: int, db: Session):
    user = db.query(Users).filter(Users.id == id, Users.status.in_([UserStatus.active, UserStatus.inactive])).first()
    if not user:
        raise HTTPException(status_code=404, detail="Can't find user or user is not active")
    
    # Cek detail di kedua tabel
    staff_detail = db.query(StaffDetails).filter(StaffDetails.users_id == id).first()
    user_detail = db.query(UserDetails).filter(UserDetails.users_id == id).first()
    
    # Tentukan detail yang ditemukan
    detail = staff_detail if staff_detail else user_detail

    # Kembalikan objek UserandDetail yang diharapkan schema
    return UserandDetail(
        id=user.id,
        username=user.username,
        status=user.status.value,
        role=user.role.value,
        name=detail.name if detail else "-",
        phone_number=detail.phone_number if detail else "-",
        address=detail.address if detail else "-"
    )

def get_staff_and_details(db: Session):
    # Get user details for all staff roles (manager, waiters, employee)
    staff_roles = [UserRole.manager, UserRole.waiters, UserRole.employee]
    
    # Ambil data dari Users, StaffDetails, dan UserDetails (backup)
    results = db.query(Users, StaffDetails, UserDetails)\
        .outerjoin(StaffDetails, Users.id == StaffDetails.users_id)\
        .outerjoin(UserDetails, Users.id == UserDetails.users_id)\
        .filter(
            Users.role.in_(staff_roles),
            Users.status.in_([UserStatus.active, UserStatus.inactive])
        ).all()
    
    staff_list = []
    for user, staff_detail, user_detail in results:
        # Gunakan staff_detail jika ada, jika tidak gunakan user_detail sebagai fallback
        detail = staff_detail if staff_detail else user_detail
        
        staff_list.append(UserandDetail(
            id=user.id,
            username=user.username,
            status=user.status.value,
            role=user.role.value,
            name=detail.name if detail else "-",
            phone_number=detail.phone_number if detail else "-",
            address=detail.address if detail else "-"
        ))
    return staff_list

def get_customers_and_details(db: Session): 
    # Get user details for all customers (use outerjoin to include those without details)
    results = db.query(Users, UserDetails)\
        .outerjoin(UserDetails, Users.id == UserDetails.users_id)\
        .filter(
            Users.role == UserRole.customer,
            Users.status.in_([UserStatus.active, UserStatus.inactive])
        ).all()
    
    customers_list = []
    for user, user_detail in results:
        customers_list.append(UserandDetail(
            id=user.id,
            username=user.username,
            status=user.status.value,
            role=user.role.value,
            name=user_detail.name if user_detail else "-",
            phone_number=user_detail.phone_number if user_detail else "-",
            address=user_detail.address if user_detail else "-"
        ))
    return customers_list   

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


