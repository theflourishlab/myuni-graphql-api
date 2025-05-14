from sqlalchemy.orm import Session
from . import models

def get_all_universities(db: Session):
    """Fetches all universities from the database"""
    return db.query(models.University).all()

# Add more specific query functions here if needed for optimization or other features
# e.g., get_universities_by_state(db: Session, state: str)