from sqlalchemy.orm import Session
from firebase_admin import auth, firestore
from app.models.user import User, UserCreate, UserRole
from app.core.security import hash_password
from app.core.firebase import get_firestore_client

db_firestore = get_firestore_client()

# Neon PostgreSQL: Get dashboard admin by email
def get_admin_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# Neon PostgreSQL: Create dashboard admin
def create_admin(db: Session, user_data: UserCreate):
    hashed_pw = hash_password(user_data.password)
    db_user = User(email=user_data.email, hashed_password=hashed_pw, role=user_data.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Firebase: List all users
def list_users():
    users = auth.list_users().iterate_all()
    user_list = []
    for user in users:
        user_data = user.__dict__.copy()
        user_data.pop("_data", None)  # Remove internal Firebase data
        user_list.append(user_data)
    return user_list

# Firebase: Create a new user
def create_user_in_firebase(email: str, password: str, role: str):
    user = auth.create_user(email=email, password=password)
    firestore_db = db_firestore.collection("users").document(user.uid)
    firestore_db.set({"email": email, "role": role, "status": "pending"})
    return user.uid

# Firebase: Update user details
def update_user_in_firebase(user_id: str, update_data: dict):
    user = auth.update_user(user_id, **update_data)
    db_firestore.collection("users").document(user_id).update(update_data)
    return user

# Firebase: Delete a user
def delete_user_in_firebase(user_id: str):
    auth.delete_user(user_id)
    db_firestore.collection("users").document(user_id).delete()
    return {"message": "User deleted"}

# Firebase: Approve user
def approve_user(user_id: str):
    db_firestore.collection("users").document(user_id).update({"status": "approved"})
    return {"message": "User approved"}

# Firebase: Put user on hold
def hold_user(user_id: str):
    db_firestore.collection("users").document(user_id).update({"status": "on_hold"})
    return {"message": "User put on hold"}

# Firebase: Generate password reset link
def generate_password_reset_link(email: str):
    return auth.generate_password_reset_link(email)
