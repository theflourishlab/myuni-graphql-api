from sqlalchemy import Column, Integer, String, TIMESTAMP, CheckConstraint, func, UniqueConstraint, Index
from sqlalchemy.sql import expression
from .database import Base

class University(Base):
    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    geopolitical_region = Column(String(50), nullable=False, index=True)
    state = Column(String(50), nullable=False, index=True)
    specialty = Column(String(100), nullable=False, index=True)
    ownership = Column(String(50), nullable=False, index=True)
    type = Column(String(50))

    academic_rigor = Column(Integer, CheckConstraint('academic rigor BETWEEN 1 AND 5'))
    sports_facilities = Column(Integer, CheckConstraint('sports_facilities BETWEEN 1 AND 5'))
    hostel_quality = Column(Integer, CheckConstraint('hostel_quality BETWEEN 1 AND 5'))
    social_life = Column(Integer, CheckConstraint('social_life BETWEEN 1 AND 5'))


    # Allow NULLD for infinity representation
    tuition_min = Column(Integer, nullable=True)
    tuition_max = Column(Integer, nullable=True)
    cost_of_living_min = Column(Integer, nullable=True)
    cost_of_living_max = Column(Integer, nullable=True)

    tuition_category_str = Column(String(100)) # Store original string
    cost_category_str = Column(String(100))

    source_url_1 = Column(String(512))
    source_url_2 = Column(String(512))

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        # Example composite index for location-based searches
        Index('ix_university_location', 'geopolitical_region', 'state'),
        # Example composite index for specialty searches within a state
        Index('ix_university_specialty_state', 'specialty', 'state'),

        # Example check constraints for data integrity
        CheckConstraint('tuition_min IS NULL OR tuition_max IS NULL OR tuition_min <= tuition_max', name='ck_tuition_range'),
        CheckConstraint('cost_of_living_min IS NULL OR cost_of_living_max IS NULL OR cost_of_living_min <= cost_of_living_max', name='ck_cost_of_living_range'),

        # Example for adding a table comment (syntax might vary slightly by DB)
        # {'comment': 'Stores information about various universities'}
    )