# app/modules/pricing/calculations/services/override_management_service.py

"""
Fixed Override Management Service - Step 7 Implementation
Handles premium calculation overrides with proper approval workflows
"""

import logging
from typing import Dict, List, Optional, Any, Union
from uuid import UUID, uuid4
from decimal import Decimal
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import BusinessLogicError, ValidationError, NotFoundError
from app.core.database import get_db

logger = logging.getLogger(__name__)


class OverrideType(str, Enum):
    """Types of premium overrides"""
    MANUAL_ADJUSTMENT = "manual_adjustment"
    RISK_OVERRIDE = "risk_override"
    COMPETITIVE_MATCH = "competitive_match"
    PROMOTIONAL = "promotional"
    UNDERWRITER_DISCRETION = "underwriter_discretion"
    REGULATORY_COMPLIANCE = "regulatory_compliance"
    SYSTEM_ERROR_CORRECTION = "system_error_correction"


class OverrideStatus(str, Enum):
    """Override approval status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ApprovalLevel(str, Enum):
    """Required approval levels"""
    AGENT = "agent"
    SUPERVISOR = "supervisor"
    MANAGER = "manager"
    UNDERWRITER = "underwriter"
    SENIOR_UNDERWRITER = "senior_underwriter"
    EXECUTIVE = "executive"


# Fixed dataclass with proper field ordering
@dataclass
class Override:
    """Override data structure - FIXED field ordering"""
    # Required fields (no defaults) come first
    override_id: UUID
    calculation_id: UUID
    original_premium: Decimal
    override_premium: Decimal
    override_type: OverrideType
    justification: str
    created_by: UUID
    expires_at: datetime
    
    # Optional fields (with defaults) come after
    status: OverrideStatus = OverrideStatus.PENDING
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


@dataclass
class ApprovalRequest:
    """Approval request data structure"""
    # Required fields first
    override_id: UUID
    decision: str  # "APPROVE" or "REJECT"
    approver_id: UUID
    
    # Optional fields with defaults
    comments: Optional[str] = None
    approval_level: ApprovalLevel = ApprovalLevel.SUPERVISOR
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class OverrideRule:
    """Override validation rules"""
    # Required fields first
    override_type: OverrideType
    max_percentage_change: Decimal
    required_approval_level: ApprovalLevel
    
    # Optional fields with defaults
    min_amount_threshold: Optional[Decimal] = None
    max_amount_threshold: Optional[Decimal] = None
    requires_documentation: bool = True
    auto_approval_enabled: bool = False
    expiry_hours: int = 24


class OverrideManagementService:
    """
    Enhanced Override Management Service for Premium Calculations
    
    Handles all aspects of premium override management including:
    - Override creation and validation
    - Approval workflow management
    - Authority level checking
    - Expiration and cleanup
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.active_overrides: Dict[UUID, Override] = {}
        self.override_rules = self._initialize_override_rules()
        
        logger.info("Override Management Service initialized")

    def _initialize_override_rules(self) -> Dict[OverrideType, OverrideRule]:
        """Initialize override validation rules"""
        return {
            OverrideType.MANUAL_ADJUSTMENT: OverrideRule(
                override_type=OverrideType.MANUAL_ADJUSTMENT,
                max_percentage_change=Decimal('10.0'),
                required_approval_level=ApprovalLevel.SUPERVISOR,
                min_amount_threshold=Decimal('100.0'),
                requires_documentation=True,
                expiry_hours=24
            ),
            OverrideType.RISK_OVERRIDE: OverrideRule(
                override_type=OverrideType.RISK_OVERRIDE,
                max_percentage_change=Decimal('25.0'),
                required_approval_level=ApprovalLevel.UNDERWRITER,
                min_amount_threshold=Decimal('500.0'),
                requires_documentation=True,
                expiry_hours=48
            ),
            OverrideType.COMPETITIVE_MATCH: OverrideRule(
                override_type=OverrideType.COMPETITIVE_MATCH,
                max_percentage_change=Decimal('15.0'),
                required_approval_level=ApprovalLevel.MANAGER,
                min_amount_threshold=Decimal('200.0'),
                requires_documentation=True,
                expiry_hours=72
            ),
            OverrideType.PROMOTIONAL: OverrideRule(
                override_type=OverrideType.PROMOTIONAL,
                max_percentage_change=Decimal('30.0'),
                required_approval_level=ApprovalLevel.MANAGER,
                requires_documentation=False,
                auto_approval_enabled=True,
                expiry_hours=168  # 7 days
            ),
            OverrideType.UNDERWRITER_DISCRETION: OverrideRule(
                override_type=OverrideType.UNDERWRITER_DISCRETION,
                max_percentage_change=Decimal('50.0'),
                required_approval_level=ApprovalLevel.SENIOR_UNDERWRITER,
                min_amount_threshold=Decimal('1000.0'),
                requires_documentation=True,
                expiry_hours=48
            ),
            OverrideType.REGULATORY_COMPLIANCE: OverrideRule(
                override_type=OverrideType.REGULATORY_COMPLIANCE,
                max_percentage_change=Decimal('100.0'),
                required_approval_level=ApprovalLevel.EXECUTIVE,
                requires_documentation=True,
                expiry_hours=24
            ),
            OverrideType.SYSTEM_ERROR_CORRECTION: OverrideRule(
                override_type=OverrideType.SYSTEM_ERROR_CORRECTION,
                max_percentage_change=Decimal('100.0'),
                required_approval_level=ApprovalLevel.MANAGER,
                requires_documentation=True,
                auto_approval_enabled=False,
                expiry_hours=12
            )
        }

    async def create_override(self, 
                            calculation_id: UUID,
                            original_premium: Decimal,
                            override_premium: Decimal,
                            override_type: OverrideType,
                            justification: str,
                            created_by: UUID,
                            metadata: Dict[str, Any] = None) -> Override:
        """Create a new premium override request"""
        try:
            # Validate override request
            await self._validate_override_request(
                original_premium, override_premium, override_type, justification
            )
            
            # Get override rules
            rule = self.override_rules.get(override_type)
            if not rule:
                raise ValidationError(f"No rules defined for override type: {override_type}")
            
            # Calculate expiration time
            expires_at = datetime.utcnow() + timedelta(hours=rule.expiry_hours)
            
            # Create override
            override = Override(
                override_id=uuid4(),
                calculation_id=calculation_id,
                original_premium=original_premium,
                override_premium=override_premium,
                override_type=override_type,
                justification=justification,
                created_by=created_by,
                expires_at=expires_at,
                metadata=metadata or {}
            )
            
            # Check for auto-approval
            if rule.auto_approval_enabled and self._qualifies_for_auto_approval(override, rule):
                override.status = OverrideStatus.APPROVED
                override.approved_at = datetime.utcnow()
                override.approved_by = created_by  # System auto-approval
                logger.info(f"Override auto-approved: {override.override_id}")
            
            # Store override
            self.active_overrides[override.override_id] = override
            
            # Log override creation
            logger.info(f"Override created: {override.override_id} for calculation: {calculation_id}")
            
            return override
            
        except Exception as e:
            logger.error(f"Error creating override: {str(e)}")
            raise BusinessLogicError(f"Failed to create override: {str(e)}")

    async def approve_override(self, approval_request: ApprovalRequest) -> Override:
        """Approve or reject an override request"""
        try:
            override = self.active_overrides.get(approval_request.override_id)
            if not override:
                raise NotFoundError(f"Override not found: {approval_request.override_id}")
            
            # Check if override is still pending
            if override.status != OverrideStatus.PENDING:
                raise ValidationError(f"Override is not pending approval: {override.status}")
            
            # Check if override has expired
            if datetime.utcnow() > override.expires_at:
                override.status = OverrideStatus.EXPIRED
                raise ValidationError("Override has expired")
            
            # Validate approval authority
            await self._validate_approval_authority(
                approval_request.approver_id, 
                override.override_type,
                approval_request.approval_level
            )
            
            # Process approval/rejection
            if approval_request.decision.upper() == "APPROVE":
                override.status = OverrideStatus.APPROVED
                override.approved_by = approval_request.approver_id
                override.approved_at = datetime.utcnow()
                logger.info(f"Override approved: {override.override_id}")
                
            elif approval_request.decision.upper() == "REJECT":
                override.status = OverrideStatus.REJECTED
                override.rejection_reason = approval_request.comments
                override.updated_at = datetime.utcnow()
                logger.info(f"Override rejected: {override.override_id}")
                
            else:
                raise ValidationError("Decision must be 'APPROVE' or 'REJECT'")
            
            # Update metadata
            if approval_request.metadata:
                override.metadata.update(approval_request.metadata)
            
            return override
            
        except Exception as e:
            logger.error(f"Error processing approval: {str(e)}")
            raise BusinessLogicError(f"Failed to process approval: {str(e)}")

    async def get_override(self, override_id: UUID) -> Optional[Override]:
        """Get override by ID"""
        return self.active_overrides.get(override_id)

    async def get_calculation_overrides(self, calculation_id: UUID) -> List[Override]:
        """Get all overrides for a specific calculation"""
        return [
            override for override in self.active_overrides.values()
            if override.calculation_id == calculation_id
        ]

    async def get_pending_overrides(self, user_id: UUID = None) -> List[Override]:
        """Get all pending overrides, optionally filtered by user"""
        pending = [
            override for override in self.active_overrides.values()
            if override.status == OverrideStatus.PENDING and datetime.utcnow() <= override.expires_at
        ]
        
        if user_id:
            pending = [o for o in pending if o.created_by == user_id]
        
        return pending

    async def cancel_override(self, override_id: UUID, cancelled_by: UUID) -> Override:
        """Cancel a pending override"""
        try:
            override = self.active_overrides.get(override_id)
            if not override:
                raise NotFoundError(f"Override not found: {override_id}")
            
            if override.status != OverrideStatus.PENDING:
                raise ValidationError("Can only cancel pending overrides")
            
            override.status = OverrideStatus.CANCELLED
            override.updated_at = datetime.utcnow()
            override.metadata['cancelled_by'] = str(cancelled_by)
            
            logger.info(f"Override cancelled: {override_id}")
            return override
            
        except Exception as e:
            logger.error(f"Error cancelling override: {str(e)}")
            raise BusinessLogicError(f"Failed to cancel override: {str(e)}")

    async def cleanup_expired_overrides(self) -> int:
        """Clean up expired overrides"""
        try:
            current_time = datetime.utcnow()
            expired_count = 0
            
            for override_id, override in list(self.active_overrides.items()):
                if (override.status == OverrideStatus.PENDING and 
                    current_time > override.expires_at):
                    override.status = OverrideStatus.EXPIRED
                    override.updated_at = current_time
                    expired_count += 1
            
            logger.info(f"Expired {expired_count} overrides")
            return expired_count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired overrides: {str(e)}")
            return 0

    # ========== VALIDATION METHODS ==========

    async def _validate_override_request(self,
                                       original_premium: Decimal,
                                       override_premium: Decimal,
                                       override_type: OverrideType,
                                       justification: str):
        """Validate override request parameters"""
        if original_premium <= 0:
            raise ValidationError("Original premium must be positive")
        
        if override_premium <= 0:
            raise ValidationError("Override premium must be positive")
        
        if not justification or len(justification.strip()) < 10:
            raise ValidationError("Justification must be at least 10 characters")
        
        # Check override rules
        rule = self.override_rules.get(override_type)
        if rule:
            percentage_change = abs((override_premium - original_premium) / original_premium * 100)
            
            if percentage_change > rule.max_percentage_change:
                raise ValidationError(
                    f"Override exceeds maximum allowed change of {rule.max_percentage_change}%"
                )
            
            if rule.min_amount_threshold and abs(override_premium - original_premium) < rule.min_amount_threshold:
                raise ValidationError(
                    f"Override amount below minimum threshold of {rule.min_amount_threshold}"
                )

    async def _validate_approval_authority(self,
                                         approver_id: UUID,
                                         override_type: OverrideType,
                                         approval_level: ApprovalLevel):
        """Validate that approver has sufficient authority"""
        rule = self.override_rules.get(override_type)
        if not rule:
            raise ValidationError(f"No rules defined for override type: {override_type}")
        
        # Define approval level hierarchy
        level_hierarchy = {
            ApprovalLevel.AGENT: 1,
            ApprovalLevel.SUPERVISOR: 2,
            ApprovalLevel.MANAGER: 3,
            ApprovalLevel.UNDERWRITER: 4,
            ApprovalLevel.SENIOR_UNDERWRITER: 5,
            ApprovalLevel.EXECUTIVE: 6
        }
        
        required_level = level_hierarchy.get(rule.required_approval_level, 0)
        approver_level = level_hierarchy.get(approval_level, 0)
        
        if approver_level < required_level:
            raise ValidationError(
                f"Insufficient approval authority. Required: {rule.required_approval_level}, "
                f"Provided: {approval_level}"
            )

    def _qualifies_for_auto_approval(self, override: Override, rule: OverrideRule) -> bool:
        """Check if override qualifies for automatic approval"""
        if not rule.auto_approval_enabled:
            return False
        
        # Calculate percentage change
        percentage_change = abs(
            (override.override_premium - override.original_premium) / 
            override.original_premium * 100
        )
        
        # Auto-approve if within smaller threshold (e.g., 5% for promotional)
        auto_approval_threshold = rule.max_percentage_change * Decimal('0.5')
        
        return percentage_change <= auto_approval_threshold

    # ========== UTILITY METHODS ==========

    async def get_override_statistics(self) -> Dict[str, Any]:
        """Get override statistics"""
        try:
            total_overrides = len(self.active_overrides)
            status_counts = {}
            type_counts = {}
            
            for override in self.active_overrides.values():
                # Count by status
                status = override.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
                
                # Count by type
                override_type = override.override_type.value
                type_counts[override_type] = type_counts.get(override_type, 0) + 1
            
            return {
                'total_overrides': total_overrides,
                'status_distribution': status_counts,
                'type_distribution': type_counts,
                'pending_count': status_counts.get('pending', 0),
                'approved_count': status_counts.get('approved', 0),
                'rejected_count': status_counts.get('rejected', 0),
                'expired_count': status_counts.get('expired', 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting override statistics: {str(e)}")
            return {}

    async def get_override_rules(self) -> Dict[OverrideType, OverrideRule]:
        """Get all override rules"""
        return self.override_rules

    async def update_override_rule(self, 
                                 override_type: OverrideType,
                                 rule_updates: Dict[str, Any]) -> OverrideRule:
        """Update override rule configuration"""
        try:
            if override_type not in self.override_rules:
                raise NotFoundError(f"Override rule not found: {override_type}")
            
            rule = self.override_rules[override_type]
            
            # Update rule attributes
            for key, value in rule_updates.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
                else:
                    logger.warning(f"Unknown rule attribute: {key}")
            
            logger.info(f"Override rule updated: {override_type}")
            return rule
            
        except Exception as e:
            logger.error(f"Error updating override rule: {str(e)}")
            raise BusinessLogicError(f"Failed to update override rule: {str(e)}")


# ========== HELPER FUNCTIONS ==========

async def get_override_management_service(db: Session = None) -> OverrideManagementService:
    """Get override management service instance"""
    if db is None:
        db = next(get_db())
    return OverrideManagementService(db)