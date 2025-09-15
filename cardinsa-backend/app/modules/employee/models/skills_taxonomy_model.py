from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime

class SkillsTaxonomy(Base):
    __tablename__ = "skills_taxonomy"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    skill_name = Column(String(255), nullable=False)
    description = Column(String)
    category_id = Column(UUID(as_uuid=True), ForeignKey("employee_skill_categories.id"))
    subcategory = Column(String(100))
    proficiency_levels = Column(String)  # or JSONB
    industry_relevance_score = Column(Integer)
    technology_dependency = Column(String)
    obsolescence_risk_score = Column(Integer)
    learning_difficulty_score = Column(Integer)
    acquisition_time_days = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    employee_skills = relationship("EmployeeSkill", back_populates="skill")