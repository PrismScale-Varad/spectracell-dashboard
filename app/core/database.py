from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from app.core.config import settings, logger  # Import logger from config
from contextlib import contextmanager

# Use environment variable for database URL
DATABASE_URL = settings.DATABASE_URL
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

# Initialize the database connection
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
        
@contextmanager
def get_db_context():
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()