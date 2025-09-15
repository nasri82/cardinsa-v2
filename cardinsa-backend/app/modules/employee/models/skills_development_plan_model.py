from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime

class SkillsDevelopmentPlan(Base):
    __tablename__ = "skills_development_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"))
    target_skill_id = Column(UUID(as_uuid=True), ForeignKey("skills_taxonomy.id"))
    development_method = Column(String)
    estimated_duration_days = Column(Integer)
    cost_estimate = Column(Numeric)
    progress_milestones = Column(Text)  # JSON or serialized structure
    mentor_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"))
    effectiveness_rating = Column(Integer)
    status = Column(String)
    completion_date = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)