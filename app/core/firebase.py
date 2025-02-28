import json
import firebase_admin
from firebase_admin import credentials, auth, firestore
import os
from app.core.config import settings, logger

# Load Firebase credentials from environment variables
FIREBASE_CREDENTIALS = settings.FIREBASE_CREDENTIALS

# Initialize Firebase only once
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS)
    firebase_admin.initialize_app(cred)
    logger.info("✅ Successfully connected to Firebase.")

# Singleton Firestore Client
_firestore_client = firestore.client()
logger.info("✅ Firestore client initialized.")

def get_firestore_client():
    """Returns a shared Firestore client instance."""
    return _firestore_client

# ---------------- FIREBASE AUTH ----------------

def get_firebase_user(email: str):
    """Retrieve a Firebase user by email."""
    try:
        return auth.get_user_by_email(email)
    except firebase_admin.auth.UserNotFoundError:
        return None
        
def get_firebase_user_by_uid(uid: str):
    """Retrieve a Firebase user by UID."""
    try:
        return auth.get_user(uid)
    except firebase_admin.auth.UserNotFoundError:
        return None
        
def create_firebase_user(email: str, password: str):
    """Creates a new Firebase user."""
    user = auth.create_user(email=email, password=password)
    logger.info(f"✅ Firebase user created: {email}")
    return user

def delete_firebase_user(user_id: str):
    """Deletes a Firebase user."""
    auth.delete_user(user_id)
    logger.info(f"🗑️ Firebase user deleted: {user_id}")

# ---------------- FIRESTORE USERS ----------------

def get_user_from_firestore(user_id: str):
    """Retrieve user document from Firestore."""
    user_doc = _firestore_client.collection("users").document(user_id).get()
    return user_doc.to_dict() if user_doc.exists else None

def create_user_in_firestore(user_id: str, update_data: dict):
    """Updates a Firestore user document."""
    _firestore_client.collection("users").document(user_id).set(update_data)
    logger.info(f"🔄 Updated Firestore user: {user_id}")

def update_user_in_firestore(user_id: str, update_data: dict):
    """Updates a Firestore user document."""
    _firestore_client.collection("users").document(user_id).update(update_data)
    logger.info(f"🔄 Updated Firestore user: {user_id}")

def delete_user_from_firestore(user_id: str):
    """Deletes a user document from Firestore."""
    _firestore_client.collection("users").document(user_id).delete()
    logger.info(f"🗑️ Firestore user deleted: {user_id}")

# ---------------- PAGINATED LIST USERS ----------------
def get_users_from_firestore(limit: int = 10, last_uid: str = None, status: str = None):
    """Retrieve a paginated list of users from Firestore with optional status filtering and total count."""
    db = get_firestore_client()
    users = []
    last_doc_id = None  # Track last document for pagination

    users_ref = db.collection("users").order_by("uid").limit(limit)

    if status:
        users_ref = db.collection("users").where("status", "==", status).order_by("uid").limit(limit)

    if last_uid:
        last_doc = db.collection("users").document(last_uid).get()
        if last_doc.exists:
            users_ref = users_ref.start_after(last_doc)

    users_stream = users_ref.stream()

    for user_doc in users_stream:
        user_data = user_doc.to_dict()
        users.append({
            "uid": user_data.get("uid", "Unknown"),
            "email": user_data.get("email", "Unknown"),
            "first_name": user_data.get("first_name", "Unknown"),
            "last_name": user_data.get("last_name", "Unknown"),
            "practice_name": user_data.get("practice_name", "Unknown"),
            "npi": user_data.get("npi", "Unknown"),
            "status": user_data.get("status", "active")
        })
        last_doc_id = user_data.get("uid")  # Store last user's UID for next page

    # 🔥 Efficient total count using Firestore aggregation query
    count_query = db.collection("users")
    if status:
        count_query = count_query.where("status", "==", status)

    total_users = count_query.count().get()[0][0].value  # Fast aggregation query for counting

    logger.info(f"📜 Retrieved {len(users)} users from Firestore with status={status or 'any'} (Total: {total_users}).")

    return {
        "users": users,
        "next_page_uid": last_doc_id,
        "total_count": total_users
    }
