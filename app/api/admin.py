from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, UserCreate, UserResponse
from app.services.user_service import get_admin_by_email, create_admin, delete_admin_by_email
from app.core.config import logger
from app.core.security import require_superadmin

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/", response_model=List[UserResponse], summary="Get all admins")
@require_superadmin
def get_all_admins(request: Request, db: Session = Depends(get_db)):
    admins = db.query(User).all()
    if not admins:
        logger.warning("No admins found")
        raise HTTPException(status_code=404, detail="No admins found")
    return admins

@router.post("/", response_model=UserResponse, summary="Create a new dashboard admin")
@require_superadmin
def add_admin(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    existing_admin = get_admin_by_email(db, user_data.email)
    if existing_admin:
        logger.warning(f"Admin already exists: {user_data.email}")
        raise HTTPException(status_code=400, detail="Admin already exists")

    new_admin = create_admin(db, user_data)
    return new_admin

@router.delete("/{email}", summary="Delete an admin by email")
@require_superadmin
def remove_admin(request: Request, email: str, db: Session = Depends(get_db)):
    try:
        response = delete_admin_by_email(db, email)
        return response
    except ValueError as e:
        logger.error(f"Failed to delete admin: {email} - {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
