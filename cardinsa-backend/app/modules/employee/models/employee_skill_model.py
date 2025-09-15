from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime

class EmployeeSkill(Base):
    __tablename__ = "employee_skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills_taxonomy.id"), nullable=False)
    current_proficiency = Column(Integer)
    score = Column(Integer)
    assessment_method = Column(String)
    validity_period_days = Column(Integer)
    development_priority = Column(String)
    certified = Column(Boolean, default=False)
    acquired_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    employee = relationship("Employee", back_populates="skills")
    skill = relationship("SkillsTaxonomy", back_populates="employee_skills")