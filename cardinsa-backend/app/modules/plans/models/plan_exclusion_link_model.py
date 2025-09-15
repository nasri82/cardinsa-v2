# app/modules/plans/models/plan_exclusion_link_model.py

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

class PlanExclusionLink(Base):
    __tablename__ = "plan_exclusion_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)
    exclusion_id = Column(UUID(as_uuid=True), ForeignKey("plan_exclusions.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    plan = relationship("Plan", back_populates="exclusions")
