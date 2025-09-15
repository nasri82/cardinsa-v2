# app/modules/insurance/quotations/models/quotation_version_model.py

from sqlalchemy import Column, Text, Integer, Boolean, DateTime, UUID, ForeignKey, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import Optional, Dict, Any
from datetime import datetime
import json


class QuotationVersion(Base):
    """
    Quotation Version model for version control and change tracking
    
    This model maintains a complete history of quotation changes,
    storing full data snapshots for each version to enable rollback
    and change comparison functionality.
    """
    __tablename__ = "quotation_versions"

    # Primary identifiers
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    quotation_id = Column(PostgresUUID(as_uuid=True), ForeignKey("quotations.id", ondelete="CASCADE"), nullable=True)
    
    # Version information
    version_number = Column(Integer, nullable=True, index=True)
    is_latest_version = Column(Boolean, nullable=False, default=True)
    
    # Complete data snapshot
    data_snapshot = Column(JSONB, nullable=True)
    
    # Audit fields
    created_by = Column(PostgresUUID(as_uuid=True), nullable=True)
    updated_by = Column(PostgresUUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(DateTime, nullable=True, onupdate=func.current_timestamp())
    archived_at = Column(DateTime, nullable=True)

    # Relationships
    quotation = relationship("Quotation", back_populates="versions")

    def __repr__(self):
        return f"<QuotationVersion(id={self.id}, quotation_id={self.quotation_id}, version_number={self.version_number})>"

    @property
    def snapshot_size(self) -> int:
        """Get the size of the data snapshot in characters"""
        if self.data_snapshot:
            return len(json.dumps(self.data_snapshot))
        return 0

    @property
    def has_snapshot(self) -> bool:
        """Check if this version has a data snapshot"""
        return self.data_snapshot is not None and len(self.data_snapshot) > 0

    def get_snapshot_field(self, field_path: str, default: Any = None) -> Any:
        """
        Get a specific field from the snapshot using dot notation
        Example: get_snapshot_field('customer.name') or get_snapshot_field('premium.total')
        """
        if not self.data_snapshot:
            return default
        
        try:
            current = self.data_snapshot
            for key in field_path.split('.'):
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default

    def set_snapshot_from_quotation(self, quotation: 'Quotation') -> None:
        """
        Create a data snapshot from a quotation object
        """
        self.data_snapshot = {
            'quotation_data': {
                'id': str(quotation.id),
                'quote_number': quotation.quote_number,
                'customer_name': quotation.customer_name,
                'customer_email': quotation.customer_email,
                'customer_phone': quotation.customer_phone,
                'status': quotation.status,
                'base_premium': float(quotation.base_premium) if quotation.base_premium else None,
                'total_premium': float(quotation.total_premium) if quotation.total_premium else None,
                'currency_code': quotation.currency_code,
                'created_at': quotation.created_at.isoformat() if quotation.created_at else None,
                'updated_at': quotation.updated_at.isoformat() if quotation.updated_at else None
            },
            'items': [
                {
                    'id': str(item.id),
                    'coverage_name': item.coverage_name,
                    'coverage_name_ar': item.coverage_name_ar,
                    'limit_amount': float(item.limit_amount) if item.limit_amount else None,
                    'notes': item.notes,
                    'display_order': item.display_order,
                    'meta_data': item.meta_data
                }
                for item in quotation.items
            ] if hasattr(quotation, 'items') and quotation.items else [],
            'factors': [
                {
                    'id': str(factor.id),
                    'key': factor.key,
                    'value': factor.value,
                    'factor_type': factor.factor_type,
                    'impact_description': factor.impact_description
                }
                for factor in quotation.factors
            ] if hasattr(quotation, 'factors') and quotation.factors else [],
            'metadata': {
                'version_created_at': datetime.utcnow().isoformat(),
                'snapshot_type': 'full_quotation'
            }
        }

    def compare_with_version(self, other_version: 'QuotationVersion') -> Dict[str, Any]:
        """
        Compare this version with another version and return differences
        """
        if not self.data_snapshot or not other_version.data_snapshot:
            return {'error': 'Cannot compare versions without data snapshots'}
        
        differences = {
            'version_comparison': {
                'from_version': other_version.version_number,
                'to_version': self.version_number,
                'comparison_date': datetime.utcnow().isoformat()
            },
            'changes': []
        }
        
        # Compare quotation data
        current_data = self.data_snapshot.get('quotation_data', {})
        other_data = other_version.data_snapshot.get('quotation_data', {})
        
        for key in set(current_data.keys()) | set(other_data.keys()):
            current_value = current_data.get(key)
            other_value = other_data.get(key)
            
            if current_value != other_value:
                differences['changes'].append({
                    'field': f'quotation.{key}',
                    'from_value': other_value,
                    'to_value': current_value,
                    'change_type': 'modified' if key in other_data and key in current_data else 
                                  'added' if key in current_data else 'removed'
                })
        
        return differences

    @classmethod
    def create_new_version(cls, quotation: 'Quotation', version_number: int = None) -> 'QuotationVersion':
        """
        Factory method to create a new version from a quotation
        """
        if version_number is None:
            # Auto-increment version number
            from sqlalchemy.orm import Session
            # This would need to be called with a session to query the max version
            version_number = 1
        
        version = cls(
            quotation_id=quotation.id,
            version_number=version_number,
            is_latest_version=True
        )
        
        version.set_snapshot_from_quotation(quotation)
        return version

    def to_dict(self) -> Dict[str, Any]:
        """Convert quotation version to dictionary representation"""
        return {
            'id': str(self.id),
            'quotation_id': str(self.quotation_id) if self.quotation_id else None,
            'version_number': self.version_number,
            'is_latest_version': self.is_latest_version,
            'has_snapshot': self.has_snapshot,
            'snapshot_size': self.snapshot_size,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'data_snapshot': self.data_snapshot
        }