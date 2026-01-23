from app.models.Staff.staff_schema import staffUpdate, staffRegister, staffResponse, staffCreate
from ormModels import Staff, staffRole, staffStatus
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password

#Fungsi Tambah Staff
def create_staff(db:Session, request:staffCreate ):
    new_staff = Staff(
        name = request.name,
        username = request.username,
        password = hash_password(request.password),
        status = request.status,
        role = request.role
    )
    db.add(new_staff)
    db.commit()
    db.refresh(new_staff)
    return new_staff

#ambil semua data staff
def get_all_staff(db:Session):
    return db.query (Staff).all()

# ambil data staff sesuai ID
def get_staff(id:int, db:Session):
    # Cek apakah ID ini benar atau engga
    staff = db.query(Staff).filter(Staff.id == id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Can't find staff")
    return staff

# Update Staff
def update_staff(id:int, request:staffUpdate, db:Session):
    # check dulu
    staff = db.query(Staff).filter(Staff.id == id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Can't find staff")
    
    # data yang ingin di ubah
    data = request.model_dump(exclude_unset=True)

    # jika di dalam data juga terdapat password baru, itu perlu di hash lagi
    if "password" in data and ["password"] is not None:
        data["password"] = hash_password[data["password"]]

    # deteksi apa aja data yang diubah
    for key, value in data.items():
        setattr(staff, key, value)

    db.commit()
    db.refresh(staff)
    return staff

# deactivate staff (soft delete)
def deactivate_staff(id: int, request:staffUpdate, db:Session):
    # check ID
    staff = db.query(Staff).filter(Staff.id == id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Can't find staff")
    
    if staff.status == "resign":
        raise HTTPException(status_code=400, detail="staff is already resigned")
    
    staff.status = staffStatus.resign
    db.commit()
    db.refresh(staff)
    return staff

# Register staff
def register_staff(db:Session, request: staffRegister):
    new_staff = Staff(
        name = request.name,
        username = request.username,
        password = hash_password(request.password),
        role = staffRole.waiters ,
        status = staffStatus.active
    )
    db.add(new_staff)
    db.commit()
    db.refresh(new_staff)
    return new_staff
