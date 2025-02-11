import jwt
from datetime import datetime, timedelta
from app.core.config import settings, pwd_context
from functools import wraps
from fastapi import Request, HTTPException

from app.models.user import UserRole

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a password against its hashed version."""
    return pwd_context.verify(plain_password, hashed_password)

# JWT Token Generation & Verification
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Generates a JWT access token for authentication."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_access_token(token: str):
    """Verifies and decodes a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token

def generate_password_reset_token(email: str) -> str:
    """
    Generates a password reset token using JWT, valid for 24 hours.
    """
    expires_delta = timedelta(hours=24)  # 24-hour expiry
    payload = {"sub": email, "exp": datetime.utcnow() + expires_delta}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_password_reset_token(token: str) -> str:
    """
    Verifies the password reset token and returns the email if valid.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload.get("sub")  # Extract email
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Reset token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid reset token")

def require_superadmin(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        admin = getattr(request.state, "user", None)

        if not admin:
            raise HTTPException(status_code=401, detail="Unauthorized access")

        if admin.role != UserRole.SUPERADMIN:  # Check if role is SUPERADMIN
            raise HTTPException(status_code=403, detail="Access denied. Superadmin privileges required.")

        return func(request=request, *args, **kwargs)

    return wrapper
