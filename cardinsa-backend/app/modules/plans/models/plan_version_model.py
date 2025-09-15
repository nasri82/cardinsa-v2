# app/modules/plans/models/plan_version_model.py

from sqlalchemy import Column, String, Date, Boolean, ForeignKey, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

class PlanVersion(Base):
    __tablename__ = "plan_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)

    version_number = Column(String, nullable=False)
    version_description = Column(Text, nullable=True)
    changes_from_previous = Column(JSONB, nullable=True)

    effective_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=True)

    created_by_reason = Column(String, nullable=True)
    regulatory_approval_required = Column(Boolean, default=False)
    approval_status = Column(String, nullable=True)
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    approved_at = Column(TIMESTAMP, nullable=True)
    is_current_version = Column(Boolean, default=False)

    created_at = Column(TIMESTAMP, nullable=True)

    # Relationships
    plan = relationship("Plan", back_populates="versions")
