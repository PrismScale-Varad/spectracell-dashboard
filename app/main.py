import os
from fastapi import FastAPI
from dotenv import load_dotenv
from app.api import admin, users
from app.core.database import init_db
# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="FastAPI Firebase Backend")

# Register routes
app.include_router(users.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "message": "API is running!",
        "environment": os.getenv("ENV", "development")  # Example check
    }

init_db()