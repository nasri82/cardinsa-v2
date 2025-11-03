"""
app/modules/benefits/services/benefit_preapproval_rule_service.py

Service for managing prior authorization and preapproval rules.
Handles complex approval workflows, authorization requirements, and decision engines.
"""

from typing import List, Optional, Dict, Any, Tuple
from decimal import Decimal
from sqlalchemy.orm import Session
from app.modules.pricing.benefits.repositories.benefit_preapproval_rule_repository import BenefitPreapprovalRuleRepository
from app.modules.pricing.benefits.models.benefit_preapproval_rule_model import BenefitPreapprovalRule
from app.core.exceptions import ValidationError, NotFoundError, BusinessLogicError
from app.core.base_service import BaseService
from app.core.logging import get_logger
from datetime import datetime, date, timedelta
from enum import Enum

logger = get_logger(__name__)


class PreapprovalDecision(str, Enum):
    """Preapproval decision types"""
    APPROVED = "approved"
    DENIED = "denied"
    PENDING = "pending"
    REQUIRES_MORE_INFO = "requires_more_info"
    PARTIALLY_APPROVED = "partially_approved"


class ApprovalType(str, Enum):
    """Approval types for compatibility"""
    PRIOR_AUTH = "PRIOR_AUTH"
    PRE_CERTIFICATION = "PRE_CERTIFICATION"
    REFERRAL = "REFERRAL"
    STEP_THERAPY = "STEP_THERAPY"


class ApprovalStatus(str, Enum):
    """Approval status for compatibility"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    EXPIRED = "EXPIRED"


class BenefitPreapprovalRuleService(BaseService):
    """Service for managing preapproval rules and authorization workflows"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = BenefitPreapprovalRuleRepository(db)
    
    async def create_preapproval_rule(self, rule_data: Dict[str, Any]) -> BenefitPreapprovalRule:
        """Create preapproval rule with validation"""
        try:
            # Validate rule data
            await self._validate_preapproval_rule_data(rule_data)
            
            # Check for conflicting rules
            await self._check_rule_conflicts(rule_data)
            
            # Set rule defaults
            rule_data = await self._set_preapproval_defaults(rule_data)
            
            # Create rule
            preapproval_rule = BenefitPreapprovalRule(**rule_data)
            created_rule = await self.repository.create(preapproval_rule)
            
            logger.info(f"Created preapproval rule: {created_rule.id}")
            return created_rule
            
        except Exception as e:
            logger.error(f"Error creating preapproval rule: {str(e)}")
            raise
    
    async def get_by_id(self, rule_id: str) -> Optional[BenefitPreapprovalRule]:
        """Get preapproval rule by ID"""
        try:
            return await self.repository.get_by_id(rule_id)
        except Exception as e:
            logger.error(f"Error getting preapproval rule {rule_id}: {str(e)}")
            raise
    
    async def update_by_id(self, rule_id: str, update_data: Dict[str, Any]) -> BenefitPreapprovalRule:
        """Update preapproval rule by ID"""
        try:
            # Get existing rule
            existing_rule = await self.repository.get_by_id(rule_id)
            if not existing_rule:
                raise NotFoundError(f"Preapproval rule not found: {rule_id}")
            
            # Validate update data
            await self._validate_update_data(update_data)
            
            # Update rule
            updated_rule = await self.repository.update(existing_rule, update_data)
            
            logger.info(f"Updated preapproval rule: {rule_id}")
            return updated_rule
            
        except Exception as e:
            logger.error(f"Error updating preapproval rule {rule_id}: {str(e)}")
            raise
    
    async def delete_by_id(self, rule_id: str) -> bool:
        """Delete preapproval rule by ID"""
        try:
            # Get existing rule
            existing_rule = await self.repository.get_by_id(rule_id)
            if not existing_rule:
                raise NotFoundError(f"Preapproval rule not found: {rule_id}")
            
            # Check if rule can be deleted
            if await self._has_active_approvals(rule_id):
                raise BusinessLogicError("Cannot delete rule with active approvals")
            
            # Delete rule
            await self.repository.delete(existing_rule)
            
            logger.info(f"Deleted preapproval rule: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting preapproval rule {rule_id}: {str(e)}")
            raise
    
    async def get_all(self) -> List[BenefitPreapprovalRule]:
        """Get all preapproval rules"""
        try:
            return await self.repository.get_all()
        except Exception as e:
            logger.error(f"Error getting all preapproval rules: {str(e)}")
            raise
    
    async def evaluate_preapproval_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate preapproval request against all applicable rules"""
        try:
            evaluation_result = {
                'request_id': request_data.get('request_id', f"REQ_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"),
                'member_id': request_data.get('member_id'),
                'benefit_type_id': request_data.get('benefit_type_id'),
                'service_details': request_data.get('service_details', {}),
                'evaluation_timestamp': datetime.utcnow(),
                'decision': PreapprovalDecision.PENDING,
                'rules_evaluated': [],
                'approval_requirements': [],
                'decision_rationale': [],
                'next_steps': [],
                'estimated_processing_time': None
            }
            
            # Get applicable preapproval rules
            benefit_schedule_id = request_data.get('benefit_schedule_id')
            if not benefit_schedule_id:
                evaluation_result['decision'] = PreapprovalDecision.APPROVED
                evaluation_result['decision_rationale'].append("No benefit schedule specified")
                evaluation_result['next_steps'].append("Proceed with service")
                return evaluation_result
            
            # Get rules for this benefit schedule
            applicable_rules = await self._get_applicable_rules(benefit_schedule_id, request_data)
            
            if not applicable_rules:
                # No preapproval required
                evaluation_result['decision'] = PreapprovalDecision.APPROVED
                evaluation_result['decision_rationale'].append("No preapproval rules applicable")
                evaluation_result['next_steps'].append("Proceed with service")
                return evaluation_result
            
            # Evaluate each applicable rule
            auto_approved = True
            requires_manual_review = False
            
            for rule in applicable_rules:
                rule_evaluation = await self._evaluate_single_preapproval_rule(rule, request_data)
                evaluation_result['rules_evaluated'].append(rule_evaluation)
                
                if rule_evaluation['requires_approval']:
                    auto_approved = False
                    
                    if rule_evaluation['auto_approvable']:
                        evaluation_result['approval_requirements'].append({
                            'rule_id': str(rule.id),
                            'approval_type': 'auto_approved',
                            'status': 'auto_approved',
                            'conditions_met': rule_evaluation['conditions_met']
                        })
                    else:
                        requires_manual_review = True
                        evaluation_result['approval_requirements'].append({
                            'rule_id': str(rule.id),
                            'approval_type': 'manual_review',
                            'status': 'requires_manual_review',
                            'missing_conditions': rule_evaluation['missing_conditions']
                        })
            
            # Determine final decision
            if auto_approved:
                evaluation_result['decision'] = PreapprovalDecision.APPROVED
                evaluation_result['decision_rationale'].append("All conditions met for auto-approval")
            elif requires_manual_review:
                evaluation_result['decision'] = PreapprovalDecision.PENDING
                evaluation_result['decision_rationale'].append("Manual review required")
                evaluation_result['estimated_processing_time'] = await self._estimate_processing_time(
                    evaluation_result['approval_requirements']
                )
            
            # Generate next steps
            evaluation_result['next_steps'] = await self._generate_next_steps(evaluation_result)
            
            return evaluation_result
            
        except Exception as e:
            logger.error(f"Error evaluating preapproval request: {str(e)}")
            raise
    
    async def get_approval_status(self, request_id: str) -> Dict[str, Any]:
        """Get current approval status and progress"""
        try:
            status_result = {
                'request_id': request_id,
                'current_status': 'PENDING',
                'progress_percentage': 0,
                'completed_steps': [],
                'pending_steps': [],
                'approver_actions': [],
                'estimated_completion': None,
                'last_updated': datetime.utcnow()
            }
            
            # This would typically query an approval requests table
            # For now, return mock data
            status_result['progress_percentage'] = 25
            status_result['estimated_completion'] = datetime.utcnow() + timedelta(days=2)
            
            return status_result
            
        except Exception as e:
            logger.error(f"Error getting approval status: {str(e)}")
            raise
    
    # Private helper methods
    async def _validate_preapproval_rule_data(self, data: Dict[str, Any]) -> None:
        """Validate preapproval rule data"""
        required_fields = ['benefit_schedule_id']
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")
    
    async def _validate_update_data(self, data: Dict[str, Any]) -> None:
        """Validate update data"""
        # Add validation logic as needed
        pass
    
    async def _check_rule_conflicts(self, data: Dict[str, Any]) -> None:
        """Check for conflicting preapproval rules"""
        benefit_schedule_id = data.get('benefit_schedule_id')
        if not benefit_schedule_id:
            return
        
        # Get existing rules for this benefit schedule
        existing_rules = self.db.query(BenefitPreapprovalRule).filter(
            BenefitPreapprovalRule.benefit_schedule_id == benefit_schedule_id,
            BenefitPreapprovalRule.is_active == True
        ).all()
        
        # Check for conflicting threshold amounts
        if 'threshold_amount' in data and data['threshold_amount']:
            threshold = Decimal(str(data['threshold_amount']))
            for existing_rule in existing_rules:
                if (existing_rule.threshold_amount and 
                    abs(existing_rule.threshold_amount - threshold) < Decimal('100')):
                    logger.warning(f"Similar threshold amount found in rule {existing_rule.id}")
    
    async def _set_preapproval_defaults(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Set default values for preapproval rule"""
        defaults = {
            'is_active': True,
            'always_required': False,
            'auto_approve_below_threshold': False,
            'effective_date': date.today(),
            'threshold_type': 'amount'
        }
        
        for key, value in defaults.items():
            if key not in data:
                data[key] = value
        
        return data
    
    async def _get_applicable_rules(self, benefit_schedule_id: str, request_data: Dict[str, Any]) -> List[BenefitPreapprovalRule]:
        """Get rules applicable to the request"""
        try:
            # Query rules for this benefit schedule
            rules = self.db.query(BenefitPreapprovalRule).filter(
                BenefitPreapprovalRule.benefit_schedule_id == benefit_schedule_id,
                BenefitPreapprovalRule.is_active == True,
                BenefitPreapprovalRule.effective_date <= date.today()
            ).filter(
                (BenefitPreapprovalRule.expiry_date.is_(None)) |
                (BenefitPreapprovalRule.expiry_date >= date.today())
            ).all()
            
            # Filter rules based on request criteria
            applicable_rules = []
            for rule in rules:
                if await self._rule_applies_to_request(rule, request_data):
                    applicable_rules.append(rule)
            
            return applicable_rules
            
        except Exception as e:
            logger.error(f"Error getting applicable rules: {str(e)}")
            return []
    
    async def _rule_applies_to_request(self, rule: BenefitPreapprovalRule, request_data: Dict[str, Any]) -> bool:
        """Check if rule applies to the request"""
        # Check provider type match if specified
        if rule.provider_type and request_data.get('provider_type'):
            if rule.provider_type != request_data['provider_type']:
                return False
        
        # Check service category match if specified
        if rule.service_category and request_data.get('service_category'):
            if rule.service_category != request_data['service_category']:
                return False
        
        return True
    
    async def _evaluate_single_preapproval_rule(self, rule: BenefitPreapprovalRule, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate single preapproval rule against request"""
        rule_evaluation = {
            'rule_id': str(rule.id),
            'rule_name': f"Rule for {rule.service_category or 'General'} services",
            'approval_type': 'preapproval',
            'requires_approval': False,
            'auto_approvable': False,
            'conditions_met': [],
            'missing_conditions': [],
            'threshold_analysis': {}
        }
        
        # Check if always required
        if rule.always_required:
            rule_evaluation['requires_approval'] = True
            rule_evaluation['conditions_met'].append("Always required for this service")
        
        # Check threshold conditions
        if rule.threshold_amount:
            service_amount = Decimal(str(request_data.get('estimated_cost', 0)))
            if service_amount >= rule.threshold_amount:
                rule_evaluation['requires_approval'] = True
                rule_evaluation['conditions_met'].append(f"Service amount ${service_amount} exceeds threshold ${rule.threshold_amount}")
            elif rule.auto_approve_below_threshold:
                rule_evaluation['auto_approvable'] = True
                rule_evaluation['conditions_met'].append(f"Service amount ${service_amount} below threshold - auto-approved")
        
        return rule_evaluation
    
    async def _estimate_processing_time(self, approval_requirements: List[Dict[str, Any]]) -> str:
        """Estimate processing time based on approval requirements"""
        manual_reviews = len([req for req in approval_requirements if req['status'] == 'requires_manual_review'])
        
        if manual_reviews == 0:
            return "Immediate"
        elif manual_reviews <= 2:
            return "1-2 business days"
        else:
            return "3-5 business days"
    
    async def _generate_next_steps(self, evaluation_result: Dict[str, Any]) -> List[str]:
        """Generate next steps based on evaluation result"""
        next_steps = []
        
        if evaluation_result['decision'] == PreapprovalDecision.APPROVED:
            next_steps.append("Preapproval granted - proceed with service")
            next_steps.append("Reference approval in claims submission")
        
        elif evaluation_result['decision'] == PreapprovalDecision.PENDING:
            next_steps.append("Submit required documentation for review")
            next_steps.append("Monitor approval status for updates")
            
            # Add specific requirements
            for requirement in evaluation_result['approval_requirements']:
                if requirement['status'] == 'requires_manual_review':
                    next_steps.append(f"Provide additional information for manual review")
        
        return next_steps
    
    async def _has_active_approvals(self, rule_id: str) -> bool:
        """Check if rule has active approvals"""
        # This would check an approvals table if it exists
        # For now, return False to allow deletion
        return False