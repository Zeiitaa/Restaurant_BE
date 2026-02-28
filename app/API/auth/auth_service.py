from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from ormModels import Users, UserDetails, UserRole, UserStatus
from app.core.auth import create_access_token, Token
from app.core.security import verify_password, hash_password
from app.models.User.user_schema import UserRegister, UserDetailCreateBase, ForgotPassword, ResetPassword, VerifyOTP
import random
import string
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def authenticate_user(db: Session, username: str, password: str) -> Users:
    """Authenticate User by username/email and Password."""
    # Check by username OR email
    user = db.query(Users).filter(
        or_(
            Users.username == username,
            Users.email == username
        )
    ).first()
    
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect username or password"
        )
    
    # Cek apakah user statusnya active atau inactive
    if user.status not in [UserStatus.active, UserStatus.inactive]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is {user.status.value} and cannot login"
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
    # Cek apakah username atau email sudah ada
    existing_user = db.query(Users).filter(
        or_(
            Users.username == request.username,
            Users.email == request.email
        )
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or Email already exists"
        )
    
    # cek apakah password sama dengan confirm password
    if request.password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Password and Confirm Password do not match")
    
    # buat data user baru
    new_User = Users(
        username = request.username,
        email = request.email,
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

# --- Forgot Password Logic ---

def send_email(to_email: str, subject: str, body: str):
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not smtp_user or not smtp_password:
        print(f"Warning: SMTP credentials not set. OTP for {to_email}: {body}")
        # In production, you might want to log this or handle it differently
        return 

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_user, to_email, text)
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send OTP email")


def forgot_password(db: Session, request: ForgotPassword):
    user = db.query(Users).filter(Users.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    
    # Generate 6-digit OTP
    otp = ''.join(random.choices(string.digits, k=6))
    
    # Set expiration time (e.g., 5 minutes from now)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
    
    # Update user with OTP
    user.otp_code = otp
    user.otp_expires_at = expires_at
    db.commit()
    
    # Send Email
    subject = "Password Reset OTP"
    body = f"Your OTP for password reset is: {otp}. It expires in 5 minutes."
    send_email(user.email, subject, body)
    
    return {"message": "OTP sent to your email"}

def verify_otp(db: Session, request: VerifyOTP):
    user = db.query(Users).filter(Users.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
        
    # Validate OTP
    if user.otp_code != request.otp_code:
        raise HTTPException(status_code=400, detail="Invalid OTP")
        
    # Check expiry
    now_utc = datetime.now(timezone.utc)
    expiry = user.otp_expires_at
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)
        
    if now_utc > expiry:
        raise HTTPException(status_code=400, detail="OTP has expired")
    
    # OTP Valid, Generate Temporary Reset Token (5 minutes valid)
    reset_token = create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(minutes=5),
        extra={"purpose": "reset_password"}
    )
    
    # Optional: Clear OTP immediately or wait until password reset
    # Keeping OTP until reset or expiry is fine, but clearing prevents replays if we wanted to enforce strict one-time use
    # For now, we rely on the short-lived token.
    user.otp_code = None
    user.otp_expires_at = None
    db.commit()
    
    return {"message": "OTP verified", "reset_token": reset_token}

def reset_password(db: Session, request: ResetPassword):
    try:
        # Decode token manually or use a dependency if available, but here we do it manually to check 'purpose'
        payload = jwt.decode(request.reset_token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        user_id = payload.get("sub")
        purpose = payload.get("purpose")
        
        if user_id is None or purpose != "reset_password":
            raise HTTPException(status_code=401, detail="Invalid reset token")
            
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired reset token")
        
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update Password
    user.password = hash_password(request.new_password)
    db.commit()
    
    return {"message": "Password has been reset successfully"}
