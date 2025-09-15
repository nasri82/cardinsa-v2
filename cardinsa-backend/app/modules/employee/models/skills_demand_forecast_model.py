from sqlalchemy import Column, Integer, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid
from datetime import datetime

class SkillsDemandForecast(Base):
    __tablename__ = "skills_demand_forecast"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills_taxonomy.id"))
    forecast_year = Column(Integer)
    projected_demand_score = Column(Integer)
    growth_rate_percentage = Column(Numeric)
    automation_threat_level = Column(Integer)
    market_emergence_notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)