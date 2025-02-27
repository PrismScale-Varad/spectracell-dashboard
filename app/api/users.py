from fastapi import APIRouter, HTTPException, Query, Body, Request
from app.services.user_service import (
    list_users,
    create_user_in_firebase,
    get_user_by_email,
    get_user_by_uid,
    update_user_in_firebase,
    delete_user_in_firebase,
    approve_user,
    hold_user,
    generate_password_reset_link
)
from app.models.firebase_user import FirebaseUser
from app.core.security import  require_superadmin

router = APIRouter(prefix="/users", tags=["Users"])

# Get paginated users
@router.get("/", summary="Get paginated users from Firestore")
def get_users(
    limit: int = Query(10, ge=1, le=100, description="Number of users per page"),
    last_uid: str = Query(None, description="UID of the last user from the previous page for pagination"),
    status: str = Query(None, regex="^(active|on_hold|all)$", description="Filter users by status (active or on_hold)"),
    email: str = None,
):
    try:
        if email:
            user = get_user_by_email(email)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user
        else:
            return list_users(limit=limit, last_uid=last_uid, status=status)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

# Get user by email
@router.get("/{email}", summary="Get user details by email")
def get_user(email: str):
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/{user_id}", summary="Get user details by UID")
def get_user_by_uid_endpoint(user_id: str):
    user = get_user_by_uid(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Create user
@router.post("/", summary="Create a new Firebase user")
def create_user(user_data: FirebaseUser):
    try:
        user_id = create_user_in_firebase(user_data)
        return {"user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error creating user")

# Update user
@router.put("/{user_id}", summary="Update user details")
def update_user(user_id: str, update_data: dict = Body(...)):
    try:
        updated_user = update_user_in_firebase(user_id, update_data)
        return updated_user
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error updating user")

# Delete user
@router.delete("/{user_id}", summary="Delete a user from Firebase")
@require_superadmin
def delete_user(request: Request, user_id: str):
    try:
        return delete_user_in_firebase(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error deleting user")

# Approve user
@router.post("/{user_id}/approve", summary="Approve and enable user")
def approve(user_id: str):
    try:
        return approve_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error approving user")

# Put user on hold
@router.post("/{user_id}/hold", summary="Put user on hold")
def hold(user_id: str):
    try:
        return hold_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error putting user on hold")

# Generate password reset link
@router.post("/password-reset", summary="Generate password reset link")
def reset_password(email: str = Body(..., embed=True)):
    try:
        return {"reset_link": generate_password_reset_link(email)}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error generating password reset link")
