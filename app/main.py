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
    allow_origins=origins,  # Allowed origins
    allow_credentials=True,  # Allow cookies and authentication headers
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
app.add_middleware(AuthMiddleware)

app.include_router(admin.router, prefix=prefix)
app.include_router(auth.router, prefix=prefix)
app.include_router(users.router, prefix=prefix)

@app.get("/")
def root():
    return {
        "message": "API is running!",
        "environment": settings.ENVIRONMENT  # Example check
    }

@app.options("/{full_path:path}")
async def preflight_request(full_path: str):
    response = Response(status_code=204)
    response.headers["Access-Control-Allow-Origin"] = ",".join(origins) if isinstance(origins, list) else origins
    response.headers["Access-Control-Allow-Methods"] = "OPTIONS, GET, POST, PUT, DELETE, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response