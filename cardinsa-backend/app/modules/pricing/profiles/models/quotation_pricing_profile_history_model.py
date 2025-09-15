# app/modules/pricing/profiles/models/quotation_pricing_profile_history_model.py
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from typing import Optional, Dict, Any, List
import uuid

from app.core.database import Base


class QuotationPricingProfileHistory(Base):
    """
    Complete audit trail for pricing profile changes.
    Tracks all modifications with full data snapshots.
    """
    __tablename__ = "quotation_pricing_profiles_history"
    __table_args__ = {'extend_existing': True}  # Allow table redefinition

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Reference to the original profile
    profile_id = Column(
        UUID(as_uuid=True),
        ForeignKey("quotation_pricing_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Audit information
    operation = Column(
        String(20), 
        nullable=False,
        comment="CREATE, UPDATE, DELETE, ARCHIVE"
    )
    changed_at = Column(DateTime, nullable=False, default=func.now())
    changed_by = Column(UUID(as_uuid=True))
    
    # Data snapshots
    old_data = Column(
        JSON,
        comment="Profile data before the change"
    )
    new_data = Column(
        JSON,
        nullable=False,
        comment="Profile data after the change"
    )
    
    # Change details
    changed_fields = Column(
        JSON,
        comment="List of fields that were modified"
    )
    change_reason = Column(
        String(500),
        comment="Business reason for the change"
    )

    def __repr__(self) -> str:
        return f"<QuotationPricingProfileHistory(profile_id={self.profile_id}, operation='{self.operation}')>"

    @property
    def summary(self) -> str:
        """Human-readable summary of the change"""
        if self.operation == "CREATE":
            return "Profile created"
        elif self.operation == "UPDATE":
            if self.changed_fields:
                fields = ", ".join(self.changed_fields)
                return f"Updated: {fields}"
            return "Profile updated"
        elif self.operation == "DELETE":
            return "Profile deleted"
        elif self.operation == "ARCHIVE":
            return "Profile archived"
        return f"Operation: {self.operation}"