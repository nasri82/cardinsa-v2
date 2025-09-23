# =============================================================================
# FILE: app/modules/underwriting/models/underwriting_workflow_model.py
# WORLD-CLASS UNDERWRITING WORKFLOW MODEL - ENTERPRISE GRADE
# =============================================================================

"""
Underwriting Workflow Model - Enterprise Implementation

Advanced workflow management system supporting:
- Configurable multi-step workflows
- Automated and manual process steps
- Conditional routing and branching
- SLA management and escalation
- Parallel and sequential processing
- Integration with business rules
"""

from sqlalchemy import Column, String, Text, Integer, Numeric, Boolean, DateTime, Date, JSON, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from uuid import uuid4
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, Dict, Any, List, Union
from enum import Enum
import json

from app.core.database import Base
from app.core.mixins import TimestampMixin, ArchiveMixin
from app.core.enums import BaseEnum


# =============================================================================
# ENUMS AND CONSTANTS
# =============================================================================

class StepType(str, BaseEnum):
    """Workflow step types"""
    AUTO = "auto"
    MANUAL = "manual"
    CONDITIONAL = "conditional"
    APPROVAL = "approval"
    NOTIFICATION = "notification"
    INTEGRATION = "integration"
    DECISION = "decision"


class StepStatus(str, BaseEnum):
    """Step execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class WorkflowStatus(str, BaseEnum):
    """Workflow execution status"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class TriggerType(str, BaseEnum):
    """Workflow trigger types"""
    APPLICATION_SUBMITTED = "application_submitted"
    STATUS_CHANGE = "status_change"
    RULE_MATCH = "rule_match"
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    API = "api"
    ESCALATION = "escalation"


class ActionType(str, BaseEnum):
    """Step action types"""
    ASSIGN = "assign"
    NOTIFY = "notify"
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_INFO = "request_info"
    ESCALATE = "escalate"
    CALCULATE = "calculate"
    INTEGRATE = "integrate"
    WAIT = "wait"


# =============================================================================
# WORKFLOW STEP DEFINITION MODEL
# =============================================================================

class UnderwritingWorkflowStep(Base, TimestampMixin, ArchiveMixin):
    """
    Workflow Step Definition Model
    
    Defines individual steps in underwriting workflows with:
    - Step configuration and requirements
    - Conditional execution logic
    - SLA and timeout management
    - Integration with external systems
    - Approval and notification handling
    """
    
    __tablename__ = 'underwriting_workflow_steps'
    
    # =========================================================================
    # PRIMARY FIELDS
    # =========================================================================
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    
    # Step Identification
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    code = Column(String(50), nullable=True, unique=True, index=True)
    
    # Step Configuration
    step_type = Column(String(20), nullable=False, default=StepType.MANUAL, index=True)
    order_index = Column(Integer, nullable=False, index=True)
    is_required = Column(Boolean, default=True, nullable=False)
    is_parallel = Column(Boolean, default=False, nullable=False)
    
    # Execution Logic
    conditions = Column(JSONB, nullable=True)  # Conditions for step execution
    actions = Column(JSONB, nullable=True)  # Actions to perform
    rules = Column(JSONB, nullable=True)  # Business rules to apply
    configuration = Column(JSONB, nullable=True)  # Step-specific configuration
    
    # Assignment and Routing
    auto_assign_to = Column(String(100), nullable=True)  # Role or user to assign to
    assignment_rules = Column(JSONB, nullable=True)  # Rules for assignment
    escalation_rules = Column(JSONB, nullable=True)  # Escalation configuration
    
    # SLA and Timing
    sla_hours = Column(Integer, nullable=True)  # SLA in hours
    timeout_hours = Column(Integer, nullable=True)  # Timeout in hours
    reminder_intervals = Column(JSONB, nullable=True)  # Reminder schedule
    
    # Dependencies
    depends_on = Column(JSONB, nullable=True)  # Steps this depends on
    blocks = Column(JSONB, nullable=True)  # Steps this blocks
    
    # Integration
    integration_config = Column(JSONB, nullable=True)  # External system integration
    notification_config = Column(JSONB, nullable=True)  # Notification settings
    
    # Metadata
    created_by = Column(UUID(as_uuid=True), nullable=True, index=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================
    
    # Workflow executions using this step
    executions = relationship("WorkflowStepExecution", back_populates="step", cascade="all, delete-orphan")
    
    # Workflow template this step belongs to
    workflow_id = Column(UUID(as_uuid=True), ForeignKey('underwriting_workflows.id'), nullable=True, index=True)
    workflow = relationship("UnderwritingWorkflow", back_populates="steps")
    
    # =========================================================================
    # CONSTRAINTS AND INDEXES
    # =========================================================================
    
    __table_args__ = (
        CheckConstraint(
            step_type.in_(['auto', 'manual', 'conditional', 'approval', 'notification', 'integration', 'decision']),
            name='ck_underwriting_workflow_step_type'
        ),
        CheckConstraint(
            'order_index >= 0',
            name='ck_underwriting_workflow_step_order_positive'
        ),
        CheckConstraint(
            'sla_hours >= 0',
            name='ck_underwriting_workflow_step_sla_positive'
        ),
        CheckConstraint(
            'timeout_hours >= 0',
            name='ck_underwriting_workflow_step_timeout_positive'
        ),
        
        # Performance indexes
        Index('ix_underwriting_workflow_steps_workflow_order', 'workflow_id', 'order_index'),
        Index('ix_underwriting_workflow_steps_type_required', 'step_type', 'is_required'),
        Index('ix_underwriting_workflow_steps_name_code', 'name', 'code'),
    )
    
    # =========================================================================
    # VALIDATION METHODS
    # =========================================================================
    
    @validates('name')
    def validate_name(self, key, value):
        """Validate step name"""
        if not value or not value.strip():
            raise ValueError("Step name is required")
        
        if len(value) > 100:
            raise ValueError("Step name cannot exceed 100 characters")
        
        return value.strip()
    
    @validates('code')
    def validate_code(self, key, value):
        """Validate step code"""
        if value:
            if len(value) > 50:
                raise ValueError("Step code cannot exceed 50 characters")
            
            # Code should be uppercase with underscores
            return value.upper().replace(' ', '_')
        
        return value
    
    @validates('order_index')
    def validate_order_index(self, key, value):
        """Validate order index"""
        if value is not None and value < 0:
            raise ValueError("Order index must be non-negative")
        return value
    
    @validates('sla_hours', 'timeout_hours')
    def validate_hours(self, key, value):
        """Validate hour fields"""
        if value is not None and value < 0:
            raise ValueError(f"{key} must be non-negative")
        return value
    
    @validates('conditions', 'actions', 'rules', 'configuration')
    def validate_json_fields(self, key, value):
        """Validate JSON structure"""
        if value is not None and not isinstance(value, dict):
            raise ValueError(f"{key} must be a valid JSON object")
        return value
    
    # =========================================================================
    # BUSINESS LOGIC METHODS
    # =========================================================================
    
    def can_execute(self, context: Dict[str, Any]) -> bool:
        """Check if step can be executed in given context"""
        if not self.conditions:
            return True
        
        try:
            return self._evaluate_conditions(self.conditions, context)
        except Exception as e:
            # Log error and default to False
            return False
    
    def get_assignment_target(self, context: Dict[str, Any]) -> Optional[str]:
        """Get assignment target based on rules"""
        if self.auto_assign_to:
            return self.auto_assign_to
        
        if self.assignment_rules:
            return self._evaluate_assignment_rules(self.assignment_rules, context)
        
        return None
    
    def get_sla_due_date(self, start_time: datetime) -> Optional[datetime]:
        """Calculate SLA due date"""
        if not self.sla_hours:
            return None
        
        return start_time + timedelta(hours=self.sla_hours)
    
    def get_timeout_date(self, start_time: datetime) -> Optional[datetime]:
        """Calculate timeout date"""
        if not self.timeout_hours:
            return None
        
        return start_time + timedelta(hours=self.timeout_hours)
    
    def get_reminder_schedule(self, start_time: datetime) -> List[datetime]:
        """Get reminder schedule"""
        if not self.reminder_intervals:
            return []
        
        reminders = []
        for interval in self.reminder_intervals:
            reminder_time = start_time + timedelta(hours=interval)
            reminders.append(reminder_time)
        
        return sorted(reminders)
    
    def should_escalate(self, execution_time: datetime) -> bool:
        """Check if step should be escalated"""
        if not self.escalation_rules:
            return False
        
        # Check if SLA is breached
        if self.sla_hours:
            sla_due = execution_time + timedelta(hours=self.sla_hours)
            if datetime.now() > sla_due:
                return True
        
        # Check custom escalation rules
        return self._evaluate_escalation_rules(self.escalation_rules, execution_time)
    
    def get_dependencies(self) -> List[str]:
        """Get list of step dependencies"""
        if not self.depends_on:
            return []
        
        if isinstance(self.depends_on, list):
            return self.depends_on
        elif isinstance(self.depends_on, dict):
            return list(self.depends_on.keys())
        
        return []
    
    def get_blocked_steps(self) -> List[str]:
        """Get list of steps blocked by this step"""
        if not self.blocks:
            return []
        
        if isinstance(self.blocks, list):
            return self.blocks
        elif isinstance(self.blocks, dict):
            return list(self.blocks.keys())
        
        return []
    
    def clone_step(self, new_name: str, created_by: UUID) -> 'UnderwritingWorkflowStep':
        """Create a copy of this step"""
        new_step = UnderwritingWorkflowStep(
            name=new_name,
            description=f"Cloned from: {self.name}",
            code=f"{self.code}_CLONE" if self.code else None,
            step_type=self.step_type,
            order_index=self.order_index,
            is_required=self.is_required,
            is_parallel=self.is_parallel,
            conditions=self.conditions.copy() if self.conditions else None,
            actions=self.actions.copy() if self.actions else None,
            rules=self.rules.copy() if self.rules else None,
            configuration=self.configuration.copy() if self.configuration else None,
            auto_assign_to=self.auto_assign_to,
            assignment_rules=self.assignment_rules.copy() if self.assignment_rules else None,
            escalation_rules=self.escalation_rules.copy() if self.escalation_rules else None,
            sla_hours=self.sla_hours,
            timeout_hours=self.timeout_hours,
            reminder_intervals=self.reminder_intervals.copy() if self.reminder_intervals else None,
            depends_on=self.depends_on.copy() if self.depends_on else None,
            blocks=self.blocks.copy() if self.blocks else None,
            integration_config=self.integration_config.copy() if self.integration_config else None,
            notification_config=self.notification_config.copy() if self.notification_config else None,
            created_by=created_by
        )
        return new_step
    
    # =========================================================================
    # PRIVATE HELPER METHODS
    # =========================================================================
    
    def _evaluate_conditions(self, conditions: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate step conditions against context"""
        # Simple condition evaluation - extend as needed
        if 'field' in conditions:
            field = conditions['field']
            operator = conditions.get('operator', 'equals')
            expected_value = conditions.get('value')
            
            actual_value = context.get(field)
            
            if operator == 'equals':
                return actual_value == expected_value
            elif operator == 'not_equals':
                return actual_value != expected_value
            elif operator == 'greater_than':
                return actual_value > expected_value
            elif operator == 'less_than':
                return actual_value < expected_value
            elif operator == 'in':
                return actual_value in expected_value
            elif operator == 'not_in':
                return actual_value not in expected_value
        
        return True
    
    def _evaluate_assignment_rules(self, rules: Dict[str, Any], context: Dict[str, Any]) -> Optional[str]:
        """Evaluate assignment rules"""
        # Simple rule evaluation - extend as needed
        if 'default' in rules:
            return rules['default']
        
        return None
    
    def _evaluate_escalation_rules(self, rules: Dict[str, Any], execution_time: datetime) -> bool:
        """Evaluate escalation rules"""
        # Simple escalation logic - extend as needed
        if 'max_hours' in rules:
            max_hours = rules['max_hours']
            elapsed_hours = (datetime.now() - execution_time).total_seconds() / 3600
            return elapsed_hours > max_hours
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'code': self.code,
            'step_type': self.step_type,
            'order_index': self.order_index,
            'is_required': self.is_required,
            'is_parallel': self.is_parallel,
            'conditions': self.conditions,
            'actions': self.actions,
            'rules': self.rules,
            'configuration': self.configuration,
            'auto_assign_to': self.auto_assign_to,
            'assignment_rules': self.assignment_rules,
            'escalation_rules': self.escalation_rules,
            'sla_hours': self.sla_hours,
            'timeout_hours': self.timeout_hours,
            'reminder_intervals': self.reminder_intervals,
            'depends_on': self.depends_on,
            'blocks': self.blocks,
            'integration_config': self.integration_config,
            'notification_config': self.notification_config,
            'workflow_id': str(self.workflow_id) if self.workflow_id else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None
        }
    
    def __repr__(self) -> str:
        return f"<UnderwritingWorkflowStep(id='{self.id}', name='{self.name}', type='{self.step_type}', order={self.order_index})>"


# =============================================================================
# WORKFLOW TEMPLATE MODEL
# =============================================================================

class UnderwritingWorkflow(Base, TimestampMixin, ArchiveMixin):
    """
    Workflow Template Model
    
    Defines complete workflow templates for different scenarios:
    - Product-specific workflows
    - Risk-based routing
    - Channel-specific processing
    - Configurable business rules
    """
    
    __tablename__ = 'underwriting_workflows'
    
    # =========================================================================
    # PRIMARY FIELDS
    # =========================================================================
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    
    # Workflow Identification
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    code = Column(String(50), nullable=True, unique=True, index=True)
    version = Column(String(20), default='1.0', nullable=False)
    
    # Workflow Configuration
    product_types = Column(JSONB, nullable=True)  # Applicable product types
    triggers = Column(JSONB, nullable=False)  # Workflow triggers
    conditions = Column(JSONB, nullable=True)  # Execution conditions
    configuration = Column(JSONB, nullable=True)  # Workflow configuration
    
    # Status and Lifecycle
    status = Column(String(20), default=WorkflowStatus.DRAFT, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_default = Column(Boolean, default=False, nullable=False)
    
    # Timing and SLA
    default_sla_hours = Column(Integer, nullable=True)
    max_duration_hours = Column(Integer, nullable=True)
    
    # Approval and Governance
    approved_by = Column(UUID(as_uuid=True), nullable=True, index=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_by = Column(UUID(as_uuid=True), nullable=True, index=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================
    
    # Workflow steps
    steps = relationship("UnderwritingWorkflowStep", back_populates="workflow", order_by="UnderwritingWorkflowStep.order_index", cascade="all, delete-orphan")
    
    # Workflow executions
    executions = relationship("WorkflowExecution", back_populates="workflow", cascade="all, delete-orphan")
    
    # Version control
    parent_workflow_id = Column(UUID(as_uuid=True), ForeignKey('underwriting_workflows.id'), nullable=True)
    child_workflows = relationship("UnderwritingWorkflow", backref="parent_workflow", remote_side=[id])
    
    # =========================================================================
    # CONSTRAINTS AND INDEXES
    # =========================================================================
    
    __table_args__ = (
        CheckConstraint(
            status.in_(['draft', 'active', 'paused', 'completed', 'failed', 'cancelled', 'archived']),
            name='ck_underwriting_workflow_status'
        ),
        CheckConstraint(
            'default_sla_hours >= 0',
            name='ck_underwriting_workflow_default_sla_positive'
        ),
        CheckConstraint(
            'max_duration_hours >= 0',
            name='ck_underwriting_workflow_max_duration_positive'
        ),
        
        # Performance indexes
        Index('ix_underwriting_workflows_product_active', 'is_active', 'is_default'),
        Index('ix_underwriting_workflows_status_active', 'status', 'is_active'),
        Index('ix_underwriting_workflows_name_version', 'name', 'version'),
    )
    
    def get_applicable_steps(self, context: Dict[str, Any]) -> List[UnderwritingWorkflowStep]:
        """Get steps applicable for given context"""
        applicable_steps = []
        
        for step in self.steps:
            if step.can_execute(context):
                applicable_steps.append(step)
        
        return applicable_steps
    
    def validate_workflow(self) -> List[str]:
        """Validate workflow configuration"""
        errors = []
        
        # Check for steps
        if not self.steps:
            errors.append("Workflow must have at least one step")
        
        # Check for duplicate order indexes
        order_indexes = [step.order_index for step in self.steps if step.order_index is not None]
        if len(order_indexes) != len(set(order_indexes)):
            errors.append("Workflow steps must have unique order indexes")
        
        # Check dependencies
        step_codes = {step.code for step in self.steps if step.code}
        for step in self.steps:
            dependencies = step.get_dependencies()
            for dep in dependencies:
                if dep not in step_codes:
                    errors.append(f"Step '{step.name}' depends on non-existent step '{dep}'")
        
        return errors
    
    def to_dict(self, include_steps: bool = False) -> Dict[str, Any]:
        """Convert to dictionary"""
        base_dict = {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'code': self.code,
            'version': self.version,
            'product_types': self.product_types,
            'triggers': self.triggers,
            'conditions': self.conditions,
            'configuration': self.configuration,
            'status': self.status,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'default_sla_hours': self.default_sla_hours,
            'max_duration_hours': self.max_duration_hours,
            'approved_by': str(self.approved_by) if self.approved_by else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None,
            'steps_count': len(self.steps) if self.steps else 0
        }
        
        if include_steps:
            base_dict['steps'] = [step.to_dict() for step in self.steps]
        
        return base_dict
    
    def __repr__(self) -> str:
        return f"<UnderwritingWorkflow(id='{self.id}', name='{self.name}', version='{self.version}', active={self.is_active})>"


# =============================================================================
# WORKFLOW EXECUTION MODELS
# =============================================================================

class WorkflowExecution(Base, TimestampMixin):
    """Workflow execution instance"""
    
    __tablename__ = 'workflow_executions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey('underwriting_workflows.id'), nullable=False, index=True)
    
    # Execution context
    application_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    profile_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    trigger_type = Column(String(30), nullable=False, index=True)
    trigger_data = Column(JSONB, nullable=True)
    
    # Execution status
    status = Column(String(20), default=WorkflowStatus.ACTIVE, nullable=False, index=True)
    current_step_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Timing
    started_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    sla_due_date = Column(DateTime(timezone=True), nullable=True)
    
    # Results
    execution_data = Column(JSONB, nullable=True)  # Runtime data
    results = Column(JSONB, nullable=True)  # Final results
    
    # Relationships
    workflow = relationship("UnderwritingWorkflow", back_populates="executions")
    step_executions = relationship("WorkflowStepExecution", back_populates="workflow_execution", cascade="all, delete-orphan")


class WorkflowStepExecution(Base, TimestampMixin):
    """Individual step execution within workflow"""
    
    __tablename__ = 'workflow_step_executions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    workflow_execution_id = Column(UUID(as_uuid=True), ForeignKey('workflow_executions.id'), nullable=False, index=True)
    step_id = Column(UUID(as_uuid=True), ForeignKey('underwriting_workflow_steps.id'), nullable=False, index=True)
    
    # Execution details
    status = Column(String(20), default=StepStatus.PENDING, nullable=False, index=True)
    assigned_to = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    sla_due_date = Column(DateTime(timezone=True), nullable=True)
    
    # Results
    input_data = Column(JSONB, nullable=True)
    output_data = Column(JSONB, nullable=True)
    execution_notes = Column(Text, nullable=True)
    error_details = Column(Text, nullable=True)
    
    # Relationships
    workflow_execution = relationship("WorkflowExecution", back_populates="step_executions")
    step = relationship("UnderwritingWorkflowStep", back_populates="executions")
    