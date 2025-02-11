import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, UserCreate, UserResponse
from app.services.user_service import get_admin_by_email, create_admin, delete_admin_by_email
from app.core.config import logger

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/{email}", response_model=UserResponse, summary="Get admin by email")
def get_admin(email: str, db: Session = Depends(get_db)):
    admin = get_admin_by_email(db, email)
    if not admin:
        logger.warning(f"Admin not found: {email}")
        raise HTTPException(status_code=404, detail="Admin not found")
    return admin

@router.post("/", response_model=UserResponse, summary="Create a new dashboard admin")
def add_admin(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_admin = get_admin_by_email(db, user_data.email)
    if existing_admin:
        logger.warning(f"Admin already exists: {user_data.email}")
        raise HTTPException(status_code=400, detail="Admin already exists")

    new_admin = create_admin(db, user_data)
    logger.info(f"Admin created: {new_admin.email}")
    return new_admin

@router.delete("/{email}", summary="Delete an admin by email")
def remove_admin(email: str, db: Session = Depends(get_db)):
    try:
        response = delete_admin_by_email(db, email)
        logger.info(f"Admin deleted: {email}")
        return response
    except ValueError as e:
        logger.error(f"Failed to delete admin: {email} - {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
