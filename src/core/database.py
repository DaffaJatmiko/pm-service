"""Database setup and session management for Performance Management System."""

from typing import Generator
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.orm import sessionmaker

from src.core.settings import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URI,
    echo=settings.SQL_ECHO,  # Show SQL queries in logs
    pool_pre_ping=True,  # Detect and reconnect to database if connection is lost
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW
)


# Dependency to get a database session
def get_db() -> Generator[Session, None, None]:
    """Dependency for getting a database session.
    
    Yields:
        Database session
        
    Notes:
        The session is closed automatically after the request is handled.
    """
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


# Function to create tables in the database
def create_db_and_tables() -> None:
    """Create database tables from SQLModel models."""
    SQLModel.metadata.create_all(engine)