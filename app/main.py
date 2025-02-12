import os
from fastapi import FastAPI, Response
from app.api import admin, auth, users
from app.core.database import init_db
from app.core.config import settings
from app.core.middleware import AuthMiddleware
from fastapi.middleware.cors import CORSMiddleware

prefix = settings.prefix
origins = settings.BACKEND_CORS_ORIGINS

init_db()
app = FastAPI(title="FastAPI Firebase Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthMiddleware)

app.include_router(admin.router, prefix=prefix)
app.include_router(auth.router, prefix=prefix)
app.include_router(users.router, prefix=prefix)

@app.get("/")
def root():
    return {
        "message": "API is running!",
        "environment": settings.ENVIRONMENT
    }

@app.head("/")
def root():
    return {}