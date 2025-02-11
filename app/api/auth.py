from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, TokenResponse, UserResponse
from app.services.auth_service import authenticate_admin, generate_admin_access_token
from app.core.security import verify_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse, summary="Admin login to get an access token")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    admin = authenticate_admin(db, user_data.email, user_data.password)
    
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = generate_admin_access_token(admin)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse, summary="Get logged-in admin details")
def get_current_admin(token: str, db: Session = Depends(get_db)):
    """Returns details of the currently logged-in admin based on JWT token."""
    payload = verify_access_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    email = payload.get("sub")
    admin = db.query(User).filter(User.email == email).first()
    
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    return admin  # Returns admin details as `UserResponse`
