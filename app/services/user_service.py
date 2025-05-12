from datetime import timedelta
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from firebase_admin import auth
from app.core.security import create_access_token, hash_password, verify_access_token, verify_password_reset_token
from app.models.firebase_user import FirebaseUser
from app.models.user import User, UserCreate, UserRole
from app.core.security import generate_password_reset_token
from app.core.firebase import (
    create_user_in_firestore,
    get_firebase_user,
    get_firebase_user_by_uid,
    get_firestore_client,
    get_user_from_firestore,
    update_user_in_firestore,
    delete_user_from_firestore,
    get_users_from_firestore,
)
from app.core.config import settings, logger
from app.services.email_service import onboarding_email, onboarding_email_admin, reset_password_email, reset_password_email_admin, send_email

db_firestore = get_firestore_client()

# Neon PostgreSQL: Get dashboard admin by email
def get_admin_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# Neon PostgreSQL: Create dashboard admin
def create_admin(db: Session, user_data: UserCreate):
    try:
        db_user = User(
            email=user_data.email,
            hashed_password=user_data.email,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Generate a password reset link
        reset_token = generate_password_reset_token(db_user.email)
        reset_link = f"{settings.FRONTEND_URL}/auth/reset-password?token={reset_token}"
        
        # Get onboarding email content for admin
        subject, body = onboarding_email_admin(db_user.email, reset_link)
        send_email(db_user.email, subject, body)

        logger.info(f"✅ Admin created: {user_data.email}")
        return db_user
    except Exception as e:
        db.rollback()
        logger.exception("❌ Error creating admin")
        raise e

def set_admin_password(db: Session, token: str, new_password: str) -> User:
    """Updates an admin's password if a valid token is provided."""
    email = verify_password_reset_token(token)
    
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    admin = get_admin_by_email(db, email)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    # Hash and update password
    admin.hashed_password = hash_password(new_password)
    db.commit()
    db.refresh(admin)
    
    return admin

def send_admin_reset_password_email(db: Session, email: str):
    """Sends a password reset email to the admin."""
    admin = get_admin_by_email(db, email)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    # Generate a reset token
    reset_token = generate_password_reset_token(email)
    reset_link = f"{settings.FRONTEND_URL}/auth/reset-password?token={reset_token}"

    # Get reset password email content for admin
    subject, body = reset_password_email_admin(email, reset_link)
    send_email(email, subject, body)

    return {"message": "Password reset email sent"}

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

# Firebase: Get user by email
def get_user_by_email(email: str) -> dict:
    """Retrieve a user's details using their email from Firebase Authentication and Firestore."""
    try:
        # Fetch user from Firebase Authentication
        firebase_user = get_firebase_user(email)
        if not firebase_user:
            return {"users": []}  # Return empty array if user not found

        # Fetch user details from Firestore
        firestore_user = get_user_from_firestore(firebase_user.uid)

        if not firestore_user:
            return {"users": []}  # Return empty array if no Firestore data

        return {"users": [firestore_user]}  # Wrap the result in a list
    except Exception as e:
        logger.exception(f"❌ Error fetching user details for email: {email}")
        raise e

def get_user_by_uid(uid: str) -> Optional[FirebaseUser]:
    """Retrieve a user's details using their UID from Firebase Authentication and Firestore."""
    try:
        # Fetch user from Firebase Authentication using UID
        firebase_user = get_firebase_user_by_uid(uid)
        if not firebase_user:
            return None

        # Fetch user details from Firestore
        firestore_user = get_user_from_firestore(firebase_user.uid)

        if not firestore_user:
            return None

        return FirebaseUser(**firestore_user)
    except Exception as e:
        logger.exception(f"❌ Error fetching user details for UID: {uid}")
        raise e

# Firebase: List users with pagination
def list_users(limit: int = 30, last_uid: str = None, status: str = None):
    try:
        if status=="all":
            users_data = get_users_from_firestore(limit=limit, last_uid=last_uid, status=None)
        else:
            users_data = get_users_from_firestore(limit=limit, last_uid=last_uid, status=status)
        return users_data
    except Exception as e:
        logger.exception("❌ Error fetching users")
        raise e

# Firebase: Create a new user
def create_user_in_firebase(user_data: FirebaseUser):
    try:
        # Create user in Firebase Authentication
        user = auth.create_user(email=user_data.email)
        logger.info("Created auth user")
        user_data = user_data.model_copy(update={"uid": user.uid, "status": "active"})

        # Store user details in Firestore
        create_user_in_firestore(user.uid, user_data.model_dump())

        # Send a password reset link
        reset_link = auth.generate_password_reset_link(user_data.email)
        
        # Get onboarding email content
        subject, body = onboarding_email(user_data.first_name, reset_link)
        send_email(user_data.email, subject, body)

        logger.info(f"✅ User created in Firebase: {user_data.email}")
        return user.uid
    except Exception as e:
        logger.exception(f"❌ Error creating Firebase user: {user_data.email}")
        raise e

# Firebase: Update user details
def update_user_in_firebase(user_id: str, update_data: dict):
    try:
        # Extract email if it needs updating in Firebase Authentication
        firebase_update_data = {}
        if "email" in update_data:
            firebase_update_data["email"] = update_data["email"]
        
        # Update email in Firebase Authentication (if present)
        if firebase_update_data:
            auth.update_user(user_id, **firebase_update_data)

        # Update remaining details in Firestore (if present)
        if update_data:
            update_user_in_firestore(user_id, update_data)

        user_doc = get_user_from_firestore(user_id)

        if not user_doc or "email" not in user_doc:
            raise ValueError(f"❌ No email found for user {user_id} in Firestore")

        updated_user = get_firebase_user(user_doc["email"])

        return updated_user
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
        # Enable user in Firebase Authentication
        auth.update_user(user_id, disabled=False)

        # Update Firestore to reflect "approved" status
        update_user_in_firestore(user_id, {"status": "active"})

        logger.info(f"✅ User approved and re-enabled: {user_id}")
        return {"message": "User approved and re-enabled"}
    except Exception as e:
        logger.exception(f"❌ Error approving user: {user_id}")
        raise e

# Firebase: Put user on hold
def hold_user(user_id: str):
    try:
        # Disable user in Firebase Authentication
        auth.update_user(user_id, disabled=True)

        # Update Firestore to reflect "on_hold" status
        update_user_in_firestore(user_id, {"status": "on_hold"})

        logger.info(f"⏸️ User put on hold and disabled: {user_id}")
        return {"message": "User put on hold and disabled"}
    except Exception as e:
        logger.exception(f"❌ Error holding user: {user_id}")
        raise e

# Firebase: Generate password reset link
def generate_password_reset_link(email: str):
    try:
        reset_link = auth.generate_password_reset_link(email)
        user = get_user_by_email(email)

        # Get reset password email content
        subject, body = reset_password_email(user['users'][0]['first_name'], reset_link)
        send_email(email, subject, body)

        logger.info(f"📩 Password reset link generated for: {email}")
        return reset_link
    except Exception as e:
        logger.exception(f"❌ Error generating password reset link for: {email}")
        raise e
