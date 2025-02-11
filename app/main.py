import os
from fastapi import FastAPI
from dotenv import load_dotenv
from app.api import admin, auth, users
from app.core.database import init_db
from app.core.config import settings
from app.core.middleware import AuthMiddleware

# Load environment variables from .env file
load_dotenv()
init_db()

app = FastAPI(title="FastAPI Firebase Backend")
app.add_middleware(AuthMiddleware)

prefix = settings.prefix

# Register routes
app.include_router(admin.router, prefix=prefix)
app.include_router(auth.router, prefix=prefix)
app.include_router(users.router, prefix=prefix)

@app.get("/")
def root():
    return {
        "message": "API is running!",
        "environment": settings.ENVIRONMENT  # Example check
    }
