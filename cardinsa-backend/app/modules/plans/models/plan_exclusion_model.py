# app/modules/plans/models/plan_exclusion_model.py

from sqlalchemy import Column, String, Date, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from app.core.database import Base
import uuid

class PlanExclusion(Base):
    __tablename__ = "plan_exclusions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exclusion_text = Column(Text, nullable=False)
    exclusion_text_ar = Column(Text, nullable=True)

    exclusion_category = Column(String, nullable=True)
    exclusion_severity = Column(String, nullable=True)
    effective_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    geographic_scope = Column(ARRAY(String), nullable=True)
    regulatory_basis = Column(String, nullable=True)
    exception_conditions = Column(JSONB, nullable=True)
