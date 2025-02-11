from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use environment variable for database URL (replace with actual Neon URL)
DATABASE_URL = os.getenv("DATABASE_URL")  
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    """Initialize database and create tables if they don't exist."""
    from app.models.user import Base  # Ensure models are loaded
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Successfully connected to PostgreSQL and initialized database.")

def get_db():
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
