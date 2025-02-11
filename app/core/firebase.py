import firebase_admin
from firebase_admin import credentials, auth, firestore
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Firebase credentials from environment variables
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS", "app/core/firebase-adminsdk.json")

# Initialize Firebase only once
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS)
    firebase_admin.initialize_app(cred)

# Singleton Firestore Client
_firestore_client = firestore.client()
logger.info("✅ Successfully connected to Firebase Firestore.")

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

def create_firebase_user(email: str, password: str):
    """Creates a new Firebase user."""
    return auth.create_user(email=email, password=password)

def delete_firebase_user(user_id: str):
    """Deletes a Firebase user."""
    auth.delete_user(user_id)

# ---------------- FIRESTORE USERS ----------------

def get_user_from_firestore(user_id: str):
    """Retrieve user document from Firestore."""
    user_doc = _firestore_client.collection("users").document(user_id).get()
    return user_doc.to_dict() if user_doc.exists else None

def update_user_in_firestore(user_id: str, update_data: dict):
    """Updates a Firestore user document."""
    _firestore_client.collection("users").document(user_id).update(update_data)

def delete_user_from_firestore(user_id: str):
    """Deletes a user document from Firestore."""
    _firestore_client.collection("users").document(user_id).delete()

# ---------------- PAGINATED LIST USERS ----------------

def get_users_from_firestore(limit: int = 10, last_uid: str = None):
    db = get_firestore_client()
    users_ref = db.collection("users").order_by("uid").limit(limit)

    if last_uid:
        last_doc = db.collection("users").document(last_uid).get()
        if last_doc.exists:
            users_ref = users_ref.start_after(last_doc)

    users_stream = users_ref.stream()

    users = []
    last_doc_id = None  # Track last document for pagination

    for user_doc in users_stream:
        user_data = user_doc.to_dict()
        users.append({
            "uid": user_data.get("uid", "Unknown"),
            "email": user_data.get("email", "Unknown"),
            "practice_name": user_data.get("practice_name", "Unknown"),
            "npi": user_data.get("npi", "Unknown"),
            "status": user_data.get("status", "active")
        })
        last_doc_id = user_data.get("uid")  # Store last user's UID for next page

    return {"users": users, "next_page_uid": last_doc_id}
