import logging
from fastapi import APIRouter, HTTPException, Query
from app.services.user_service import list_users
from app.core.config import logger

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", summary="Get paginated users from Firestore")
def get_users(
    limit: int = Query(10, ge=1, le=100, description="Number of users per page"),
    last_uid: str = Query(None, description="UID of the last user from the previous page for pagination"),
):
    try:
        return list_users(limit=limit, last_uid=last_uid)
    except Exception as e:
        logger.exception("Failed to fetch users")  # Logs the full stack trace
        raise HTTPException(status_code=500, detail="Internal server error")
