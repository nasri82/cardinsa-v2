from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid
from datetime import datetime

class SkillsGapAnalysis(Base):
    __tablename__ = "skills_gap_analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"))
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills_taxonomy.id"))
    current_level = Column(Integer)
    required_level = Column(Integer)
    gap_severity_score = Column(Integer)
    impact_analysis = Column(Text)
    recommended_actions = Column(Text)
    implementation_timeline = Column(Text)
    budget_estimate = Column(Numeric)
    success_metrics = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)