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
from app.core.config import logger

db_firestore = get_firestore_client()

# Neon PostgreSQL: Get dashboard admin by email
def get_admin_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# Neon PostgreSQL: Create dashboard admin
def create_admin(db: Session, user_data: UserCreate):
    if user_data.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise ValueError("Invalid role. Only 'admin' or 'superadmin' are allowed.")

    try:
        hashed_pw = hash_password(user_data.password)
        db_user = User(
            email=user_data.email,
            hashed_password=hashed_pw
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"✅ Admin created: {user_data.email}")
        return db_user
    except Exception as e:
        db.rollback()
        logger.exception("❌ Error creating admin")
        raise e

# Neon PostgreSQL: Delete dashboard admin by email
def delete_admin_by_email(db: Session, email: str):
    admin = db.query(User).filter(User.email == email).first()
    if not admin:
        raise ValueError("Admin not found")
    
    try:
        db.delete(admin)
        db.commit()
        logger.info(f"🗑️ Admin deleted: {email}")
        return {"message": f"Admin with email {email} has been deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.exception("❌ Error deleting admin")
        raise e

# Firebase: List users with pagination
def list_users(page: int = 1, limit: int = 30, last_uid: str = None):
    try:
        return get_users_from_firestore(limit=limit, last_uid=last_uid)
    except Exception as e:
        logger.exception("❌ Error fetching users")
        return {"error": "Failed to fetch users"}

# Firebase: Create a new user
def create_user_in_firebase(email: str, password: str, role: str):
    try:
        user = auth.create_user(email=email, password=password)
        update_user_in_firestore(user.uid, {"email": email, "role": role, "status": "pending"})
        logger.info(f"✅ User created in Firebase: {email}")
        return user.uid
    except Exception as e:
        logger.exception(f"❌ Error creating Firebase user: {email}")
        raise e

# Firebase: Update user details
def update_user_in_firebase(user_id: str, update_data: dict):
    try:
        auth.update_user(user_id, **update_data)
        update_user_in_firestore(user_id, update_data)
        logger.info(f"✅ User updated: {user_id}")
        return {"message": "User updated"}
    except Exception as e:
        logger.exception(f"❌ Error updating Firebase user: {user_id}")
        raise e

# Firebase: Delete a user
def delete_user_in_firebase(user_id: str):
    try:
        auth.delete_user(user_id)
        delete_user_from_firestore(user_id)
        logger.info(f"🗑️ User deleted: {user_id}")
        return {"message": "User deleted"}
    except Exception as e:
        logger.exception(f"❌ Error deleting Firebase user: {user_id}")
        raise e

# Firebase: Approve user
def approve_user(user_id: str):
    try:
        update_user_in_firestore(user_id, {"status": "approved"})
        logger.info(f"✅ User approved: {user_id}")
        return {"message": "User approved"}
    except Exception as e:
        logger.exception(f"❌ Error approving user: {user_id}")
        raise e

# Firebase: Put user on hold
def hold_user(user_id: str):
    try:
        update_user_in_firestore(user_id, {"status": "on_hold"})
        logger.info(f"⏸️ User put on hold: {user_id}")
        return {"message": "User put on hold"}
    except Exception as e:
        logger.exception(f"❌ Error holding user: {user_id}")
        raise e

# Firebase: Generate password reset link
def generate_password_reset_link(email: str):
    try:
        reset_link = auth.generate_password_reset_link(email)
        logger.info(f"📩 Password reset link generated for: {email}")
        return reset_link
    except Exception as e:
        logger.exception(f"❌ Error generating password reset link for: {email}")
        raise e
