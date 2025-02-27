from fastapi import APIRouter, Body, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, UserLogin, TokenResponse, UserResponse
from app.services.auth_service import authenticate_admin, generate_admin_access_token
from app.services.user_service import send_admin_reset_password_email, set_admin_password
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
async def get_current_admin(request: Request):
    """Returns details of the currently logged-in admin based on JWT token."""
    return request.state.user

@router.post("/reset-password", summary="Set password for an admin using a token")
def set_admin_password_endpoint(
    db: Session = Depends(get_db),
    token: str = Body(...),
    new_password: str = Body(...)
):
    return set_admin_password(db, token, new_password)

@router.post("/reset-password/request", summary="Request password reset")
def request_password_reset(
    data: dict = Body(...), 
    db: Session = Depends(get_db)
):
    return send_admin_reset_password_email(db, data["email"])
