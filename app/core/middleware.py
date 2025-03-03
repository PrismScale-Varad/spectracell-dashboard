from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from app.core.security import verify_access_token
from app.core.database import get_db_context
from app.models.user import User
from app.core.config import EXCLUDED_ROUTES, logger

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.exclude_routes = EXCLUDED_ROUTES

    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)

        if request.url.path in self.exclude_routes:
            return await call_next(request)  # Skip authentication for excluded routes

        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Missing or invalid token"})

        token = auth_header.split(" ")[1]
        payload = verify_access_token(token)
        if not payload:
            return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})

        email = payload.get("sub")
        
        with get_db_context() as db:
            admin = db.query(User).filter(User.email == email).first()

            if not admin:
                return JSONResponse(status_code=404, content={"detail": "Admin not found"})

            # Verify if the token matches the one stored in the database
            if admin.session_token != token:
                return JSONResponse(status_code=401, content={"detail": "Session expired or invalid"})

            request.state.user = admin  # Store admin in request state

        response = await call_next(request)
        return response
