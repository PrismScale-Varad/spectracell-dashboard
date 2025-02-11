from sqlalchemy.orm import Session
from firebase_admin import auth
from app.models.user import User, UserCreate, UserRole
from app.core.security import hash_password
from app.core.firebase import (
    get_firestore_client,
    update_user_in_firestore,
    delete_user_from_firestore,
    get_users_from_firestore,
)

db_firestore = get_firestore_client()

# Neon PostgreSQL: Get dashboard admin by email
def get_admin_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# Neon PostgreSQL: Create dashboard admin
def create_admin(db: Session, user_data: UserCreate):
    if user_data.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise ValueError("Invalid role. Only 'admin' or 'superadmin' are allowed.")

    hashed_pw = hash_password(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_pw,
        role=user_data.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Neon PostgreSQL: Delete dashboard admin by email
def delete_admin_by_email(db: Session, email: str):
    admin = db.query(User).filter(User.email == email).first()
    if not admin:
        raise ValueError("Admin not found")
    
    db.delete(admin)
    db.commit()
    return {"message": f"Admin with email {email} has been deleted successfully"}

# Firebase: List users with pagination
def list_users(page: int = 1, limit: int = 30, last_uid: str = None):
    try:
        return get_users_from_firestore(limit=limit, last_uid=last_uid)
    except Exception as e:
        print(f"Error fetching users: {e}")
        return {"error": "Failed to fetch users"}

# Firebase: Create a new user
def create_user_in_firebase(email: str, password: str, role: str):
    user = auth.create_user(email=email, password=password)
    update_user_in_firestore(user.uid, {"email": email, "role": role, "status": "pending"})
    return user.uid

# Firebase: Update user details
def update_user_in_firebase(user_id: str, update_data: dict):
    auth.update_user(user_id, **update_data)
    update_user_in_firestore(user_id, update_data)
    return {"message": "User updated"}

# Firebase: Delete a user
def delete_user_in_firebase(user_id: str):
    auth.delete_user(user_id)
    delete_user_from_firestore(user_id)
    return {"message": "User deleted"}

# Firebase: Approve user
def approve_user(user_id: str):
    update_user_in_firestore(user_id, {"status": "approved"})
    return {"message": "User approved"}

# Firebase: Put user on hold
def hold_user(user_id: str):
    update_user_in_firestore(user_id, {"status": "on_hold"})
    return {"message": "User put on hold"}

# Firebase: Generate password reset link
def generate_password_reset_link(email: str):
    return auth.generate_password_reset_link(email)
