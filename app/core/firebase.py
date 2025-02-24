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
    """Retrieve a paginated list of users from Firestore with optional status filtering."""
    db = get_firestore_client()
    users = []
    last_doc_id = None  # Track last document for pagination

    if status == "active":
        # Get users where status is NOT "on_hold"
        users_ref_active = db.collection("users").where("status", "!=", "on_hold").order_by("uid").limit(limit)

        # Get all users and filter out those where "status" is missing
        users_ref_missing = db.collection("users").order_by("uid").limit(limit)  

        if last_uid:
            last_doc = db.collection("users").document(last_uid).get()
            if last_doc.exists:
                users_ref_active = users_ref_active.start_after(last_doc)
                users_ref_missing = users_ref_missing.start_after(last_doc)

        # Fetch both sets of users
        users_stream_active = list(users_ref_active.stream())
        users_stream_missing = [
            doc for doc in users_ref_missing.stream() if "status" not in doc.to_dict()
        ]

        users_stream = users_stream_active + users_stream_missing  # Merge both results
    elif status == "on_hold":
        users_ref = db.collection("users").where("status", "==", "on_hold").order_by("uid").limit(limit)

        if last_uid:
            last_doc = db.collection("users").document(last_uid).get()
            if last_doc.exists:
                users_ref = users_ref.start_after(last_doc)

        users_stream = users_ref.stream()
    else:
        users_ref = db.collection("users").order_by("uid").limit(limit)
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
            "practice_name": user_data.get("practice_name", "Unknown"),
            "npi": user_data.get("npi", "Unknown"),
            "status": user_data.get("status", "active")  # Default to "active" if missing
        })
        last_doc_id = user_data.get("uid")  # Store last user's UID for next page

    logger.info(f"📜 Retrieved {len(users)} users from Firestore with status={status or 'any'}.")
    return {"users": users, "next_page_uid": last_doc_id}

