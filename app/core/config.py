import os
import logging
from pydantic_settings import BaseSettings
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()
class Settings(BaseSettings):
    # API Route prefix
    prefix: str="/api/v1"

    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/mydatabase")

    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "secret")
    SECURITY_PASSWORD_SALT: str = os.getenv("SECURITY_PASSWORD_SALT", "salt")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

    # CORS settings
    BACKEND_CORS_ORIGINS: list[str] = ['http://localhost:3000','http://localhost']
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # Firebase settings (if applicable)
    FIREBASE_CREDENTIALS: str = os.getenv("FIREBASE_CREDENTIALS")

    # Logger settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

    ENVIRONMENT: str = os.getenv("ENV", "DEVELOPMENT").upper()

    # RESEND
    SENDER_ADDRESS: str = os.getenv("FROM_SENDER_ADDRESS")
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY")

# Initialize settings
settings = Settings()

# ✅ Common password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Initialize logger
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

EXCLUDED_ROUTES = {
    "/",
    "/api/v1/auth/login",
    "/api/v1/auth/reset-password",
    "/api/v1/auth/reset-password/request",
    "/docs",
    "/redoc",
    "/openapi.json",
}
