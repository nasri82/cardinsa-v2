# app/modules/insurance/quotations/models/quotation_audit_log_model.py

from sqlalchemy import Column, String, Text, DateTime, UUID, ForeignKey, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class AuditActionType(str, Enum):
    """Enumeration for audit action types"""
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    VIEW = "VIEW"
    EXPORT = "EXPORT"
    PRINT = "PRINT"
    SEND = "SEND"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    LOCK = "LOCK"
    UNLOCK = "UNLOCK"
    CALCULATE = "CALCULATE"
    CONVERT = "CONVERT"
    ARCHIVE = "ARCHIVE"
    RESTORE = "RESTORE"
    LOGIN_ACCESS = "LOGIN_ACCESS"
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"
    DATA_BREACH_ATTEMPT = "DATA_BREACH_ATTEMPT"


class QuotationAuditLog(Base):
    """
    Quotation Audit Log model for comprehensive audit trail
    
    This model provides detailed audit logging for all quotation-related
    activities, supporting compliance requirements, security monitoring,
    and forensic analysis with comprehensive change tracking.
    """
    __tablename__ = "quotation_audit_log"

    # Primary identifiers
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    quotation_id = Column(PostgresUUID(as_uuid=True), ForeignKey("quotations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # User and session information
    user_id = Column(PostgresUUID(as_uuid=True), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True, index=True)  # Supports both IPv4 and IPv6
    
    # Action details
    action_type = Column(String(50), nullable=False, index=True)
    action_details = Column(Text, nullable=True)
    
    # Change tracking
    changed_values = Column(JSONB, nullable=True)
    
    # Timestamp (immutable for audit integrity)
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())

    # Relationships
    quotation = relationship("Quotation", back_populates="audit_logs")

    def __repr__(self):
        return f"<QuotationAuditLog(id={self.id}, action_type={self.action_type}, user_id={self.user_id})>"

    @property
    def is_security_event(self) -> bool:
        """Check if this is a security-related event"""
        security_actions = [
            AuditActionType.UNAUTHORIZED_ACCESS,
            AuditActionType.DATA_BREACH_ATTEMPT,
            AuditActionType.LOGIN_ACCESS
        ]
        return self.action_type in security_actions

    @property
    def is_data_modification(self) -> bool:
        """Check if this action modified data"""
        modification_actions = [
            AuditActionType.CREATE,
            AuditActionType.UPDATE,
            AuditActionType.DELETE,
            AuditActionType.ARCHIVE,
            AuditActionType.RESTORE
        ]
        return self.action_type in modification_actions

    @property
    def is_business_action(self) -> bool:
        """Check if this is a business workflow action"""
        business_actions = [
            AuditActionType.APPROVE,
            AuditActionType.REJECT,
            AuditActionType.CALCULATE,
            AuditActionType.CONVERT,
            AuditActionType.SEND
        ]
        return self.action_type in business_actions

    @property
    def risk_level(self) -> str:
        """Determine the risk level of this audit event"""
        if self.action_type in [AuditActionType.DATA_BREACH_ATTEMPT, AuditActionType.UNAUTHORIZED_ACCESS]:
            return "HIGH"
        elif self.action_type in [AuditActionType.DELETE, AuditActionType.EXPORT]:
            return "MEDIUM"
        elif self.is_data_modification:
            return "LOW"
        else:
            return "INFO"

    def get_changed_field_names(self) -> List[str]:
        """Get a list of field names that were changed"""
        if not self.changed_values:
            return []
        
        fields = []
        for key, value in self.changed_values.items():
            if isinstance(value, dict) and 'old' in value and 'new' in value:
                fields.append(key)
            else:
                fields.append(key)
        return fields

    def get_field_change(self, field_name: str) -> Optional[Dict[str, Any]]:
        """Get the before/after values for a specific field"""
        if not self.changed_values or field_name not in self.changed_values:
            return None
        
        change = self.changed_values[field_name]
        if isinstance(change, dict) and 'old' in change and 'new' in change:
            return change
        else:
            return {'new': change, 'old': None}

    @classmethod
    def create_audit_log(cls, quotation_id: str, user_id: str, action_type: str,
                        action_details: str = None, changed_values: Dict = None,
                        ip_address: str = None) -> 'QuotationAuditLog':
        """
        Factory method to create an audit log entry
        """
        return cls(
            quotation_id=quotation_id,
            user_id=user_id,
            action_type=action_type,
            action_details=action_details,
            changed_values=changed_values,
            ip_address=ip_address
        )

    @classmethod
    def create_creation_log(cls, quotation_id: str, user_id: str, 
                           ip_address: str = None) -> 'QuotationAuditLog':
        """
        Factory method to create a creation audit log
        """
        return cls.create_audit_log(
            quotation_id=quotation_id,
            user_id=user_id,
            action_type=AuditActionType.CREATE,
            action_details="Quotation created",
            ip_address=ip_address
        )

    @classmethod
    def create_update_log(cls, quotation_id: str, user_id: str, changed_fields: Dict,
                         action_details: str = None, ip_address: str = None) -> 'QuotationAuditLog':
        """
        Factory method to create an update audit log
        """
        return cls.create_audit_log(
            quotation_id=quotation_id,
            user_id=user_id,
            action_type=AuditActionType.UPDATE,
            action_details=action_details or f"Updated fields: {', '.join(changed_fields.keys())}",
            changed_values=changed_fields,
            ip_address=ip_address
        )

    @classmethod
    def create_security_log(cls, quotation_id: str, action_type: str, user_id: str = None,
                           ip_address: str = None, details: str = None) -> 'QuotationAuditLog':
        """
        Factory method to create a security audit log
        """
        return cls.create_audit_log(
            quotation_id=quotation_id,
            user_id=user_id,
            action_type=action_type,
            action_details=details,
            ip_address=ip_address
        )

    def add_changed_field(self, field_name: str, old_value: Any, new_value: Any) -> None:
        """Add a changed field to the audit log"""
        if self.changed_values is None:
            self.changed_values = {}
        
        self.changed_values[field_name] = {
            'old': old_value,
            'new': new_value,
            'changed_at': datetime.utcnow().isoformat()
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert quotation audit log to dictionary representation"""
        return {
            'id': str(self.id),
            'quotation_id': str(self.quotation_id),
            'user_id': str(self.user_id) if self.user_id else None,
            'action_type': self.action_type,
            'action_details': self.action_details,
            'changed_values': self.changed_values,
            'changed_field_names': self.get_changed_field_names(),
            'ip_address': self.ip_address,
            'is_security_event': self.is_security_event,
            'is_data_modification': self.is_data_modification,
            'is_business_action': self.is_business_action,
            'risk_level': self.risk_level,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }