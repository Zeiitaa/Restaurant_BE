from database import sessionLocal
from ormModels import Users, UserRole

def check_users():
    db = sessionLocal()
    try:
        users = db.query(Users).all()
        print(f"{'ID':<5} | {'Username':<15} | {'Role (Enum)':<15} | {'Role (Raw Value)':<15}")
        print("-" * 60)
        for user in users:
            # Accessing the raw value of the Enum column
            raw_role = user.role.value if hasattr(user.role, 'value') else user.role
            print(f"{user.id:<5} | {user.username:<15} | {str(user.role):<15} | {str(raw_role):<15}")
            
        print("\nChecking specifically for ID 10 (or last user):")
        test_user = db.query(Users).filter(Users.id == 10).first()
        if not test_user:
             test_user = db.query(Users).order_by(Users.id.desc()).first()
             
        if test_user:
            print(f"User ID: {test_user.id}")
            print(f"Username: {test_user.username}")
            print(f"Role object: {test_user.role}")
            print(f"Role type: {type(test_user.role)}")
            
            staff_roles = [UserRole.manager, UserRole.waiters, UserRole.employee]
            is_staff = test_user.role in staff_roles
            print(f"Is in staff_roles? {is_staff}")
            print(f"Staff roles defined as: {[r for r in staff_roles]}")
        else:
            print("No users found.")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
