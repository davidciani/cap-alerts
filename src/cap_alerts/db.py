"""db.py - Database setup stuff."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """A SQLAlchemy declarative base class for the app."""
