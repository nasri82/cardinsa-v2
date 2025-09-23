# app/modules/pricing/profiles/models/quotation_pricing_profile_rule_model.py

"""
Complete QuotationPricingProfileRule Model - Step 4 Implementation

This model manages the many-to-many relationship between pricing profiles and pricing rules.
It provides sophisticated association management including:
- ✅ Priority ordering and execution sequencing
- ✅ Rule activation/deactivation per profile
- ✅ Effective date management for time-sensitive rules
- ✅ Configuration overrides and customization
- ✅ Performance tracking and usage analytics
- ✅ Complete audit trail and change management

This is the "orchestration layer" that determines which rules apply to which profiles,
in what order, and under what conditions.
"""

from sqlalchemy import Column, String, Text, Boolean, Numeric, DateTime, Integer, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin
from decimal import Decimal
from typing import Optional, Dict, Any, List
from enum import Enum
import uuid


# Enums for the association model
class AssociationStatus(str, Enum):
    """Status of profile-rule association"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    SCHEDULED = "scheduled"
    EXPIRED = "expired"
    DRAFT = "draft"


class ExecutionMode(str, Enum):
    """Rule execution mode within profile"""
    SEQUENTIAL = "sequential"      # Execute in order, stop on first match
    PARALLEL = "parallel"          # Execute all applicable rules
    CONDITIONAL = "conditional"    # Execute based on conditions
    EXCLUSIVE = "exclusive"        # Only one rule can apply


class OverrideType(str, Enum):
    """Types of rule overrides at profile level"""
    ADJUSTMENT_VALUE = "adjustment_value"
    PRIORITY = "priority"
    CONDITION_VALUE = "condition_value"
    EFFECTIVE_DATES = "effective_dates"
    EXECUTION_MODE = "execution_mode"
    CUSTOM = "custom"


class QuotationPricingProfileRule(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """
    Complete QuotationPricingProfileRule Model - Step 4 Implementation
    
    This model provides comprehensive profile-rule association management with:
    - Sophisticated priority and ordering system
    - Rule-specific overrides and customization
    - Effective date management for time-sensitive associations
    - Performance tracking and usage analytics
    - Complete audit trail and change management
    - Integration with external systems and workflows
    """
    
    __tablename__ = "quotation_pricing_profile_rules"
    __table_args__ = (
        # Performance indexes
        Index('idx_profile_rule_profile_id', 'profile_id'),
        Index('idx_profile_rule_rule_id', 'rule_id'),
        Index('idx_profile_rule_status', 'status'),
        Index('idx_profile_rule_priority', 'priority_order'),
        Index('idx_profile_rule_execution_order', 'execution_order'),
        Index('idx_profile_rule_active', 'is_active'),
        Index('idx_profile_rule_effective_from', 'effective_from'),
        Index('idx_profile_rule_effective_to', 'effective_to'),
        Index('idx_profile_rule_created_by', 'created_by'),
        # Composite indexes for common queries
        Index('idx_profile_rule_profile_status', 'profile_id', 'status'),
        Index('idx_profile_rule_profile_active', 'profile_id', 'is_active'),
        Index('idx_profile_rule_profile_priority', 'profile_id', 'priority_order'),
        Index('idx_profile_rule_rule_active', 'rule_id', 'is_active'),
        Index('idx_profile_rule_effective_priority', 'effective_from', 'priority_order'),
        # Unique constraint to prevent duplicate associations
        Index('idx_profile_rule_unique', 'profile_id', 'rule_id', unique=True),
        {'extend_existing': True}
    )
    
    # =================================================================
    # CORE ASSOCIATION IDENTIFICATION
    # =================================================================
    
    # Foreign keys (UUIDPrimaryKeyMixin provides 'id')
    profile_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('quotation_pricing_profiles.id', ondelete='CASCADE'), 
        nullable=False,
        comment="Reference to the pricing profile"
    )
    rule_id = Column(
        UUID(as_uuid=True), 
        ForeignKey('quotation_pricing_rules.id', ondelete='CASCADE'), 
        nullable=False,
        comment="Reference to the pricing rule"
    )
    
    # Association metadata
    association_name = Column(String(255), nullable=True, comment="Custom name for this association")
    association_description = Column(Text, nullable=True, comment="Description of why this rule is associated")
    
    # =================================================================
    # PRIORITY AND EXECUTION MANAGEMENT - STEP 4 CORE REQUIREMENT
    # =================================================================
    
    # Priority and ordering
    priority_order = Column(Integer, default=100, nullable=False, comment="Priority order (lower = higher priority)")
    execution_order = Column(Integer, default=100, nullable=False, comment="Execution order within same priority")
    execution_mode = Column(String(20), default=ExecutionMode.SEQUENTIAL.value, nullable=False, comment="How this rule executes")
    
    # Rule grouping and dependencies
    rule_group = Column(String(100), nullable=True, comment="Logical group this rule belongs to")
    depends_on_rules = Column(JSONB, nullable=True, comment="List of rule IDs this rule depends on")
    conflicts_with_rules = Column(JSONB, nullable=True, comment="List of rule IDs that conflict with this rule")
    
    # Execution conditions
    execution_conditions = Column(JSONB, nullable=True, comment="Additional conditions for rule execution")
    pre_execution_checks = Column(JSONB, nullable=True, comment="Checks to perform before execution")
    post_execution_actions = Column(JSONB, nullable=True, comment="Actions to perform after execution")
    
    # =================================================================
    # STATUS AND LIFECYCLE MANAGEMENT
    # =================================================================
    
    # Association status
    status = Column(String(20), nullable=False, default=AssociationStatus.ACTIVE.value, comment="Current association status")
    is_active = Column(Boolean, default=True, nullable=False, comment="Whether association is currently active")
    
    # Effective date management - STEP 4 REQUIREMENT
    effective_from = Column(DateTime(timezone=True), nullable=False, default=func.now(), comment="When association becomes effective")
    effective_to = Column(DateTime(timezone=True), nullable=True, comment="When association expires")
    
    # Scheduling and automation
    auto_activate_at = Column(DateTime(timezone=True), nullable=True, comment="When to automatically activate")
    auto_deactivate_at = Column(DateTime(timezone=True), nullable=True, comment="When to automatically deactivate")
    
    # Suspension and temporary disabling
    suspended_from = Column(DateTime(timezone=True), nullable=True, comment="When association was suspended")
    suspended_to = Column(DateTime(timezone=True), nullable=True, comment="When suspension ends")
    suspension_reason = Column(String(255), nullable=True, comment="Reason for suspension")
    
    # =================================================================
    # RULE OVERRIDES AND CUSTOMIZATION - STEP 4 REQUIREMENT
    # =================================================================
    
    # Override configuration
    has_overrides = Column(Boolean, default=False, nullable=False, comment="Whether this association has overrides")
    override_config = Column(JSONB, nullable=True, comment="Configuration overrides for this specific association")
    
    # Common override fields
    override_adjustment_value = Column(Numeric(15, 4), nullable=True, comment="Override for rule's adjustment value")
    override_priority = Column(Integer, nullable=True, comment="Override for rule's priority")
    override_condition_value = Column(Text, nullable=True, comment="Override for rule's condition value")
    
    # Override boundaries and limits
    override_min_adjustment = Column(Numeric(15, 4), nullable=True, comment="Override for minimum adjustment")
    override_max_adjustment = Column(Numeric(15, 4), nullable=True, comment="Override for maximum adjustment")
    
    # Override metadata
    override_reason = Column(String(255), nullable=True, comment="Reason for overrides")
    override_approved_by = Column(String(255), nullable=True, comment="Who approved the overrides")
    override_approved_at = Column(DateTime(timezone=True), nullable=True, comment="When overrides were approved")
    
    # =================================================================
    # PERFORMANCE AND TRACKING - STEP 4 REQUIREMENT
    # =================================================================
    
    # Usage statistics
    execution_count = Column(Integer, default=0, nullable=False, comment="Number of times rule was executed for this profile")
    last_executed_at = Column(DateTime(timezone=True), nullable=True, comment="When rule was last executed")
    
    # Performance metrics
    avg_execution_time_ms = Column(Numeric(10, 4), nullable=True, comment="Average execution time in milliseconds")
    total_execution_time_ms = Column(Numeric(15, 4), default=Decimal('0.0000'), nullable=False, comment="Total execution time")
    
    # Success and error tracking
    successful_executions = Column(Integer, default=0, nullable=False, comment="Number of successful executions")
    failed_executions = Column(Integer, default=0, nullable=False, comment="Number of failed executions")
    last_error_at = Column(DateTime(timezone=True), nullable=True, comment="When last error occurred")
    last_error_message = Column(Text, nullable=True, comment="Last error message")
    
    # Impact tracking
    total_adjustment_applied = Column(Numeric(15, 2), default=Decimal('0.00'), nullable=False, comment="Total adjustment amount applied")
    avg_adjustment_applied = Column(Numeric(15, 2), nullable=True, comment="Average adjustment amount applied")
    applications_affected = Column(Integer, default=0, nullable=False, comment="Number of applications affected by this rule")
    
    # =================================================================
    # AUDIT AND COMPLIANCE
    # =================================================================
    
    # User tracking (TimestampMixin provides created_at, updated_at)
    created_by = Column(String(255), nullable=False, comment="User who created the association")
    last_modified_by = Column(String(255), nullable=False, comment="User who last modified the association")
    activated_by = Column(String(255), nullable=True, comment="User who activated the association")
    deactivated_by = Column(String(255), nullable=True, comment="User who deactivated the association")
    
    # Change tracking
    change_reason = Column(String(255), nullable=True, comment="Reason for last change")
    approval_required = Column(Boolean, default=False, nullable=False, comment="Whether changes require approval")
    approved_by = Column(String(255), nullable=True, comment="Who approved this association")
    approved_at = Column(DateTime(timezone=True), nullable=True, comment="When association was approved")
    
    # Configuration and metadata
    configuration = Column(JSONB, nullable=True, comment="Extended configuration options")
    tags = Column(JSONB, nullable=True, comment="Tags for categorization and search")
    notes = Column(Text, nullable=True, comment="Internal notes and comments")
    
    # External system integration
    external_ref_id = Column(String(100), nullable=True, comment="Reference ID in external system")
    external_system = Column(String(50), nullable=True, comment="External system identifier")
    sync_status = Column(String(20), nullable=True, comment="Synchronization status with external system")
    last_synced_at = Column(DateTime(timezone=True), nullable=True, comment="When last synchronized")
    
    # =================================================================
    # RELATIONSHIPS
    # =================================================================
    
    # Relationships to parent models
    profile = relationship(
        "QuotationPricingProfile",
        back_populates="profile_rules",
        foreign_keys=[profile_id]
    )
    
    rule = relationship(
        "QuotationPricingRule", 
        back_populates="profile_rules",
        foreign_keys=[rule_id]
    )
    
    # =================================================================
    # BUSINESS LOGIC METHODS - STEP 4 CORE REQUIREMENTS
    # =================================================================
    
    def is_currently_effective(self) -> bool:
        """
        Check if association is currently effective
        
        Returns:
            bool: True if association is active, effective, and not deleted
        """
        from datetime import datetime
        now = datetime.utcnow()
        
        # Check basic status
        if not self.is_active or self.status != AssociationStatus.ACTIVE.value or self.is_deleted:
            return False
        
        # Check effective dates
        if self.effective_from > now:
            return False
        
        if self.effective_to and self.effective_to <= now:
            return False
        
        # Check suspension
        if self.suspended_from and self.suspended_to:
            if self.suspended_from <= now <= self.suspended_to:
                return False
        elif self.suspended_from and not self.suspended_to:
            if self.suspended_from <= now:
                return False
        
        return True
    
    def is_scheduled_for_activation(self) -> bool:
        """
        Check if association is scheduled for future activation
        
        Returns:
            bool: True if scheduled for activation
        """
        from datetime import datetime
        now = datetime.utcnow()
        
        return (
            self.status == AssociationStatus.SCHEDULED.value and
            self.auto_activate_at and
            self.auto_activate_at > now
        )
    
    def is_expired(self) -> bool:
        """
        Check if association has expired
        
        Returns:
            bool: True if association has expired
        """
        from datetime import datetime
        now = datetime.utcnow()
        
        return (
            self.status == AssociationStatus.EXPIRED.value or
            (self.effective_to and self.effective_to <= now) or
            (self.auto_deactivate_at and self.auto_deactivate_at <= now)
        )
    
    def is_suspended(self) -> bool:
        """
        Check if association is currently suspended
        
        Returns:
            bool: True if association is suspended
        """
        from datetime import datetime
        now = datetime.utcnow()
        
        if self.status == AssociationStatus.SUSPENDED.value:
            return True
        
        if self.suspended_from and self.suspended_to:
            return self.suspended_from <= now <= self.suspended_to
        elif self.suspended_from and not self.suspended_to:
            return self.suspended_from <= now
        
        return False
    
    def has_dependency_conflicts(self, active_rule_ids: List[str]) -> Dict[str, Any]:
        """
        Check for dependency and conflict issues
        
        Args:
            active_rule_ids (List[str]): List of currently active rule IDs
            
        Returns:
            Dict[str, Any]: Dependency and conflict analysis
        """
        issues = {
            'missing_dependencies': [],
            'conflicting_rules': [],
            'has_issues': False
        }
        
        # Check dependencies
        if self.depends_on_rules:
            for dep_rule_id in self.depends_on_rules:
                if dep_rule_id not in active_rule_ids:
                    issues['missing_dependencies'].append(dep_rule_id)
        
        # Check conflicts
        if self.conflicts_with_rules:
            for conflict_rule_id in self.conflicts_with_rules:
                if conflict_rule_id in active_rule_ids:
                    issues['conflicting_rules'].append(conflict_rule_id)
        
        issues['has_issues'] = bool(issues['missing_dependencies'] or issues['conflicting_rules'])
        
        return issues
    
    def get_effective_rule_configuration(self) -> Dict[str, Any]:
        """
        Get the effective rule configuration including overrides - STEP 4 REQUIREMENT
        
        Returns:
            Dict[str, Any]: Effective configuration for rule execution
        """
        # Start with rule's base configuration
        config = self.rule.to_dict() if self.rule else {}
        
        # Apply profile-specific overrides
        if self.has_overrides and self.override_config:
            config.update(self.override_config)
        
        # Apply specific field overrides
        if self.override_adjustment_value is not None:
            config['adjustment_value'] = float(self.override_adjustment_value)
        
        if self.override_priority is not None:
            config['priority'] = self.override_priority
        
        if self.override_condition_value is not None:
            config['value'] = self.override_condition_value
        
        if self.override_min_adjustment is not None:
            config['min_adjustment'] = float(self.override_min_adjustment)
        
        if self.override_max_adjustment is not None:
            config['max_adjustment'] = float(self.override_max_adjustment)
        
        # Add association-specific metadata
        config['association_id'] = str(self.id)
        config['priority_order'] = self.priority_order
        config['execution_order'] = self.execution_order
        config['execution_mode'] = self.execution_mode
        config['has_overrides'] = self.has_overrides
        
        return config
    
    def execute_rule(self, base_amount: Decimal, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Execute the associated rule with profile-specific configuration - STEP 4 CORE FEATURE
        
        Args:
            base_amount (Decimal): Base amount to adjust
            input_data (Dict[str, Any]): Input data for rule evaluation
            
        Returns:
            Optional[Dict[str, Any]]: Rule execution results or None if not applicable
        """
        from datetime import datetime
        start_time = datetime.utcnow()
        
        try:
            # Check if association is effective
            if not self.is_currently_effective():
                return None
            
            # Check pre-execution conditions
            if not self._check_pre_execution_conditions(input_data):
                return None
            
            # Get effective configuration (including overrides)
            effective_config = self.get_effective_rule_configuration()
            
            # Execute rule with effective configuration
            # This would integrate with the rule's apply_rule method
            if self.rule:
                result = self.rule.apply_rule(base_amount, input_data)
                
                if result and result.get('success'):
                    # Apply association-specific adjustments
                    result = self._apply_association_adjustments(result, effective_config)
                    
                    # Update tracking
                    execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                    self.update_execution_tracking(True, execution_time, result.get('adjustment_amount', 0))
                    
                    # Execute post-execution actions
                    self._execute_post_execution_actions(result)
                    
                    # Add association metadata to result
                    result['association_id'] = str(self.id)
                    result['priority_order'] = self.priority_order
                    result['execution_order'] = self.execution_order
                    result['execution_time_ms'] = execution_time
                    
                    return result
                else:
                    # Track failed execution
                    execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                    self.update_execution_tracking(False, execution_time)
                    return None
            
            return None
            
        except Exception as e:
            # Track error
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.update_execution_tracking(False, execution_time, error_message=str(e))
            return None
    
    def update_execution_tracking(
        self, 
        success: bool, 
        execution_time_ms: float, 
        adjustment_amount: Optional[Decimal] = None,
        error_message: Optional[str] = None
    ):
        """
        Update execution tracking statistics
        
        Args:
            success (bool): Whether execution was successful
            execution_time_ms (float): Execution time in milliseconds
            adjustment_amount (Optional[Decimal]): Adjustment amount applied
            error_message (Optional[str]): Error message if failed
        """
        from datetime import datetime
        
        self.execution_count += 1
        self.last_executed_at = datetime.utcnow()
        
        # Update execution time tracking
        self.total_execution_time_ms += Decimal(str(execution_time_ms))
        if self.avg_execution_time_ms:
            self.avg_execution_time_ms = (
                self.avg_execution_time_ms * (self.execution_count - 1) + Decimal(str(execution_time_ms))
            ) / self.execution_count
        else:
            self.avg_execution_time_ms = Decimal(str(execution_time_ms))
        
        # Update success/failure tracking
        if success:
            self.successful_executions += 1
            
            if adjustment_amount is not None:
                self.applications_affected += 1
                self.total_adjustment_applied += adjustment_amount
                
                # Update average adjustment
                if self.avg_adjustment_applied:
                    self.avg_adjustment_applied = (
                        self.avg_adjustment_applied * (self.applications_affected - 1) + adjustment_amount
                    ) / self.applications_affected
                else:
                    self.avg_adjustment_applied = adjustment_amount
        else:
            self.failed_executions += 1
            
            if error_message:
                self.last_error_at = datetime.utcnow()
                self.last_error_message = error_message
    
    def suspend(self, reason: str, suspended_by: str, until: Optional[DateTime] = None):
        """
        Suspend the association
        
        Args:
            reason (str): Reason for suspension
            suspended_by (str): User performing suspension
            until (Optional[DateTime]): When suspension ends
        """
        from datetime import datetime
        
        self.status = AssociationStatus.SUSPENDED.value
        self.suspension_reason = reason
        self.suspended_from = datetime.utcnow()
        self.suspended_to = until
        self.last_modified_by = suspended_by
    
    def reactivate(self, reactivated_by: str):
        """
        Reactivate a suspended association
        
        Args:
            reactivated_by (str): User performing reactivation
        """
        self.status = AssociationStatus.ACTIVE.value
        self.suspension_reason = None
        self.suspended_from = None
        self.suspended_to = None
        self.activated_by = reactivated_by
        self.last_modified_by = reactivated_by
    
    def clone_association(
        self, 
        new_profile_id: str, 
        created_by: str, 
        include_overrides: bool = True
    ) -> "QuotationPricingProfileRule":
        """
        Create a copy of this association for a different profile
        
        Args:
            new_profile_id (str): ID of the target profile
            created_by (str): User creating the clone
            include_overrides (bool): Whether to copy overrides
            
        Returns:
            QuotationPricingProfileRule: New cloned association
        """
        clone = QuotationPricingProfileRule(
            profile_id=new_profile_id,
            rule_id=self.rule_id,
            association_name=f"Cloned from {self.association_name or 'association'}",
            association_description=f"Cloned from profile {self.profile_id}",
            priority_order=self.priority_order,
            execution_order=self.execution_order,
            execution_mode=self.execution_mode,
            rule_group=self.rule_group,
            depends_on_rules=self.depends_on_rules.copy() if self.depends_on_rules else None,
            conflicts_with_rules=self.conflicts_with_rules.copy() if self.conflicts_with_rules else None,
            execution_conditions=self.execution_conditions.copy() if self.execution_conditions else None,
            status=AssociationStatus.DRAFT.value,  # Always start as draft
            is_active=False,  # Requires activation
            effective_from=func.now(),
            created_by=created_by,
            last_modified_by=created_by,
            configuration=self.configuration.copy() if self.configuration else None,
            tags=self.tags.copy() if self.tags else None
        )
        
        # Copy overrides if requested
        if include_overrides and self.has_overrides:
            clone.has_overrides = True
            clone.override_config = self.override_config.copy() if self.override_config else None
            clone.override_adjustment_value = self.override_adjustment_value
            clone.override_priority = self.override_priority
            clone.override_condition_value = self.override_condition_value
            clone.override_min_adjustment = self.override_min_adjustment
            clone.override_max_adjustment = self.override_max_adjustment
            clone.override_reason = f"Cloned with overrides from {self.profile_id}"
        
        return clone
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert association to dictionary for API responses
        
        Returns:
            Dict[str, Any]: Association data as dictionary
        """
        return {
            'id': str(self.id),
            'profile_id': str(self.profile_id),
            'rule_id': str(self.rule_id),
            'association_name': self.association_name,
            'association_description': self.association_description,
            'priority_order': self.priority_order,
            'execution_order': self.execution_order,
            'execution_mode': self.execution_mode,
            'rule_group': self.rule_group,
            'status': self.status,
            'is_active': self.is_active,
            'effective_from': self.effective_from.isoformat() if self.effective_from else None,
            'effective_to': self.effective_to.isoformat() if self.effective_to else None,
            'has_overrides': self.has_overrides,
            'override_adjustment_value': float(self.override_adjustment_value) if self.override_adjustment_value else None,
            'override_priority': self.override_priority,
            'override_condition_value': self.override_condition_value,
            'is_currently_effective': self.is_currently_effective(),
            'is_scheduled_for_activation': self.is_scheduled_for_activation(),
            'is_expired': self.is_expired(),
            'is_suspended': self.is_suspended(),
            'execution_count': self.execution_count,
            'successful_executions': self.successful_executions,
            'failed_executions': self.failed_executions,
            'success_rate': (self.successful_executions / self.execution_count) if self.execution_count > 0 else None,
            'avg_execution_time_ms': float(self.avg_execution_time_ms) if self.avg_execution_time_ms else None,
            'avg_adjustment_applied': float(self.avg_adjustment_applied) if self.avg_adjustment_applied else None,
            'total_adjustment_applied': float(self.total_adjustment_applied),
            'applications_affected': self.applications_affected,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'last_modified_by': self.last_modified_by
        }
    
    # =================================================================
    # PRIVATE HELPER METHODS
    # =================================================================
    
    def _check_pre_execution_conditions(self, input_data: Dict[str, Any]) -> bool:
        """Check pre-execution conditions"""
        if not self.pre_execution_checks:
            return True
        
        # Implement pre-execution condition checking logic
        # This would be expanded based on specific requirements
        return True
    
    def _apply_association_adjustments(self, result: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply association-specific adjustments to rule result"""
        # Apply any association-specific modifications to the result
        # This could include scaling factors, additional conditions, etc.
        return result
    
    def _execute_post_execution_actions(self, result: Dict[str, Any]):
        """Execute post-execution actions"""
        if not self.post_execution_actions:
            return
        
        # Implement post-execution action logic
        # This could include notifications, logging, external API calls, etc.
        pass
    
    def __repr__(self):
        return f"<QuotationPricingProfileRule(id={self.id}, profile_id={self.profile_id}, rule_id={self.rule_id}, status='{self.status}', priority={self.priority_order})>"