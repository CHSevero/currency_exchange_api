"""Database connection and session management module.

This module provides the core database functionality including:
- Database engine configuration
- Session management
- Base model class
- Dependency for database operations
"""

from collections.abc import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


class DatabaseManager:
    """Manages database connections and sessions."""

    def __init__(self) -> None:
        """Initialize the database manager with the configured database URI."""
        database_url = f"sqlite:///./{settings.DATABASE_NAME}"
        self.engine = create_engine(database_url, connect_args={"check_same_thread": False})
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_db(self) -> Generator:
        """Create a new database session.

        Yields:
            Generator: A database session that should be closed after use.
        """
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def set_engine(self, new_engine: Engine) -> None:
        """Set a new database engine.

        Args:
            new_engine: The new SQLAlchemy engine to set.
        """
        self.engine = new_engine
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_engine(self) -> Generator:
        """Get the current database engine.

        Returns:
            Generator: The current SQLAlchemy engine.
        """
        return self.engine


# Create a sigle instance of DatabaseManager
database_manager = DatabaseManager()

# Base class for SQLAlchemy models
Base = declarative_base()


# Expose get_db as a module-level function
def get_db() -> Generator:
    """Get a database session from the database manager.

    Yields:
        Generator: A database session that should be closed after use.
    """
    yield database_manager.get_db()


def get_engine() -> Generator:
    """Get the current database engine from the database manager.

    Returns:
        Generator: The current SQLAlchemy engine.
    """
    yield database_manager.get_engine()


def set_engine(new_engine: Engine) -> None:
    """Set a new database engine in the database manager.

    Args:
        new_engine: The new SQLAlchemy engine to set.
    """
    database_manager.set_engine(new_engine)
