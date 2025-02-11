import firebase_admin
from firebase_admin import credentials, auth, firestore
import os

# Load Firebase credentials from environment variables
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS", "firebase-adminsdk.json")

# Initialize Firebase if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS)
    firebase_admin.initialize_app(cred)

# Firestore client
def get_firestore_client():
    return firestore.client()

# Firebase Auth: Get user by email
def get_firebase_user(email: str):
    try:
        return auth.get_user_by_email(email)
    except firebase_admin.auth.UserNotFoundError:
        return None

# Firebase Auth: Create a user
def create_firebase_user(email: str, password: str):
    return auth.create_user(email=email, password=password)

# Firebase Auth: Delete a user
def delete_firebase_user(user_id: str):
    auth.delete_user(user_id)

# Firestore: Get user document
def get_user_from_firestore(user_id: str):
    db = get_firestore_client()
    return db.collection("users").document(user_id).get().to_dict()

# Firestore: Update user document
def update_user_in_firestore(user_id: str, update_data: dict):
    db = get_firestore_client()
    db.collection("users").document(user_id).update(update_data)

# Firestore: Delete user document
def delete_user_from_firestore(user_id: str):
    db = get_firestore_client()
    db.collection("users").document(user_id).delete()
