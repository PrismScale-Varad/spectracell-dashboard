from datetime import timedelta
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import verify_password, create_access_token, hash_password, verify_access_token
from app.services.user_service import get_admin_by_email
from app.core.config import settings

def authenticate_admin(db: Session, email: str, password: str) -> User | None:
    """Authenticates an admin using email and password."""
    admin = get_admin_by_email(db, email)
    if not admin or not verify_password(password, admin.hashed_password):
        return None
    return admin

def generate_admin_access_token(admin: User) -> str:
    """Generates a JWT token for an authenticated admin."""
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_access_token({"sub": admin.email}, expires_delta)

def save_session_token(db: Session, user: User, token: str) -> bool:
    """
    Saves the given session token for the user in the database.
    If the operation is successful, returns True; otherwise, returns False.
    """
    try:
        user.session_token = token  # Assign the provided token
        db.commit()  # Save changes
        db.refresh(user)  # Refresh user object
        return True
    except Exception:
        db.rollback()  # Roll back in case of an error
        return False
