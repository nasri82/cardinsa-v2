# app/modules/pricing/plans/services/plan_eligibility_rule_service.py
"""
Plan Eligibility Rule Service

Business logic layer for Plan Eligibility Rule operations.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date, datetime

from app.modules.pricing.plans.repositories.plan_eligibility_rule_repository import PlanEligibilityRuleRepository
from app.modules.pricing.plans.schemas.plan_eligibility_rule_schema import (
    PlanEligibilityRuleCreate,
    PlanEligibilityRuleUpdate,
    PlanEligibilityRuleResponse,
    BulkEligibilityRuleCreate,
    EligibilityRuleSummary,
    EligibilityRuleSearchFilters,
    EligibilityEvaluationRequest,
    EligibilityEvaluationResponse,
    RuleEvaluationResult
)
from app.modules.pricing.plans.models.plan_eligibility_rule_model import (
    RuleCategory,
    RuleType,
    RuleSeverity
)
from app.core.exceptions import EntityNotFoundError, BusinessLogicError, ValidationError
import logging

logger = logging.getLogger(__name__)

class PlanEligibilityRuleService:
    """Service layer for Plan Eligibility Rule operations"""
    
    def __init__(self, repository: PlanEligibilityRuleRepository):
        self.repository = repository
    
    def create_eligibility_rule(
        self,
        plan_id: UUID,
        rule_data: PlanEligibilityRuleCreate,
        created_by: UUID
    ) -> PlanEligibilityRuleResponse:
        """Create new eligibility rule"""
        # Validate rule name doesn't already exist for plan
        existing = self.repository.get_by_plan_and_name(
            plan_id, rule_data.rule_name
        )
        if existing:
            raise ValidationError(f"Rule name '{rule_data.rule_name}' already exists for this plan")
        
        create_dict = rule_data.dict()
        create_dict['plan_id'] = plan_id
        
        eligibility_rule = self.repository.create(create_dict, created_by)
        
        # Add computed fields
        response = PlanEligibilityRuleResponse.from_orm(eligibility_rule)
        response.is_effective = eligibility_rule.is_effective()
        response.has_child_rules = len(eligibility_rule.child_rules) > 0
        
        return response
    
    def bulk_create_eligibility_rules(
        self,
        plan_id: UUID,
        bulk_data: BulkEligibilityRuleCreate,
        created_by: UUID
    ) -> List[PlanEligibilityRuleResponse]:
        """Bulk create eligibility rules"""
        # Validate no duplicate rule names in request
        rule_names = [rule.rule_name for rule in bulk_data.rules]
        if len(rule_names) != len(set(rule_names)):
            raise ValidationError("Duplicate rule names in request")
        
        # Check for existing rule names
        existing_names = []
        for rule_name in rule_names:
            if self.repository.get_by_plan_and_name(plan_id, rule_name):
                existing_names.append(rule_name)
        
        if existing_names:
            raise ValidationError(f"Rule names already exist: {', '.join(existing_names)}")
        
        rules_data = []
        for rule in bulk_data.rules:
            rule_dict = rule.dict()
            rule_dict['plan_id'] = plan_id
            rules_data.append(rule_dict)
        
        eligibility_rules = self.repository.bulk_create(rules_data, created_by)
        
        responses = []
        for rule in eligibility_rules:
            response = PlanEligibilityRuleResponse.from_orm(rule)
            response.is_effective = rule.is_effective()
            response.has_child_rules = len(rule.child_rules) > 0
            responses.append(response)
        
        return responses
    
    def get_eligibility_rule(self, rule_id: UUID) -> PlanEligibilityRuleResponse:
        """Get eligibility rule by ID"""
        eligibility_rule = self.repository.get_by_id(rule_id)
        if not eligibility_rule:
            raise EntityNotFoundError(f"Eligibility rule {rule_id} not found")
        
        response = PlanEligibilityRuleResponse.from_orm(eligibility_rule)
        response.is_effective = eligibility_rule.is_effective()
        response.has_child_rules = len(eligibility_rule.child_rules) > 0
        
        return response
    
    def get_plan_eligibility_rules(
        self,
        plan_id: UUID,
        filters: Optional[EligibilityRuleSearchFilters] = None
    ) -> List[PlanEligibilityRuleResponse]:
        """Get eligibility rules for a plan with filters"""
        if not filters:
            filters = EligibilityRuleSearchFilters()
        
        eligibility_rules = self.repository.get_by_plan(
            plan_id=plan_id,
            rule_category=filters.rule_category,
            rule_type=filters.rule_type,
            rule_severity=filters.rule_severity,
            is_mandatory=filters.is_mandatory,
            is_active=filters.is_active,
            can_override=filters.can_override,
            rule_group=filters.rule_group,
            effective_date=filters.effective_date,
            text_search=filters.text_search,
            tags=filters.tags
        )
        
        responses = []
        for rule in eligibility_rules:
            response = PlanEligibilityRuleResponse.from_orm(rule)
            response.is_effective = rule.is_effective()
            response.has_child_rules = len(rule.child_rules) > 0
            responses.append(response)
        
        return responses
    
    def get_effective_eligibility_rules(
        self,
        plan_id: UUID,
        check_date: Optional[date] = None
    ) -> List[PlanEligibilityRuleResponse]:
        """Get effective eligibility rules for a plan"""
        eligibility_rules = self.repository.get_effective_rules(plan_id, check_date)
        
        responses = []
        for rule in eligibility_rules:
            response = PlanEligibilityRuleResponse.from_orm(rule)
            response.is_effective = True  # Already filtered for effective
            response.has_child_rules = len(rule.child_rules) > 0
            responses.append(response)
        
        return responses
    
    def get_mandatory_eligibility_rules(self, plan_id: UUID) -> List[PlanEligibilityRuleResponse]:
        """Get mandatory eligibility rules for a plan"""
        eligibility_rules = self.repository.get_mandatory_rules(plan_id)
        
        responses = []
        for rule in eligibility_rules:
            response = PlanEligibilityRuleResponse.from_orm(rule)
            response.is_effective = rule.is_effective()
            response.has_child_rules = len(rule.child_rules) > 0
            responses.append(response)
        
        return responses
    
    def get_rules_by_category(
        self,
        plan_id: UUID,
        category: RuleCategory
    ) -> List[PlanEligibilityRuleResponse]:
        """Get eligibility rules by category"""
        eligibility_rules = self.repository.get_by_category(plan_id, category)
        
        responses = []
        for rule in eligibility_rules:
            response = PlanEligibilityRuleResponse.from_orm(rule)
            response.is_effective = rule.is_effective()
            response.has_child_rules = len(rule.child_rules) > 0
            responses.append(response)
        
        return responses
    
    def update_eligibility_rule(
        self,
        rule_id: UUID,
        update_data: PlanEligibilityRuleUpdate,
        updated_by: UUID
    ) -> PlanEligibilityRuleResponse:
        """Update eligibility rule"""
        eligibility_rule = self.repository.get_by_id(rule_id)
        if not eligibility_rule:
            raise EntityNotFoundError(f"Eligibility rule {rule_id} not found")
        
        # Validate rule name uniqueness if being updated
        if update_data.rule_name and update_data.rule_name != eligibility_rule.rule_name:
            existing = self.repository.get_by_plan_and_name(
                eligibility_rule.plan_id, update_data.rule_name
            )
            if existing:
                raise ValidationError(f"Rule name '{update_data.rule_name}' already exists for this plan")
        
        update_dict = update_data.dict(exclude_unset=True, exclude_none=True)
        updated = self.repository.update(rule_id, update_dict, updated_by)
        
        if not updated:
            raise BusinessLogicError("Failed to update eligibility rule")
        
        response = PlanEligibilityRuleResponse.from_orm(updated)
        response.is_effective = updated.is_effective()
        response.has_child_rules = len(updated.child_rules) > 0
        
        return response
    
    def delete_eligibility_rule(self, rule_id: UUID) -> bool:
        """Delete eligibility rule"""
        success = self.repository.delete(rule_id)
        if not success:
            raise EntityNotFoundError(f"Eligibility rule {rule_id} not found")
        return success
    
    def evaluate_eligibility(
        self,
        plan_id: UUID,
        evaluation_request: EligibilityEvaluationRequest
    ) -> EligibilityEvaluationResponse:
        """Evaluate plan eligibility for an applicant"""
        # Get effective rules for the plan
        effective_rules = self.repository.get_effective_rules(
            plan_id, evaluation_request.check_date
        )
        
        if not effective_rules:
            return EligibilityEvaluationResponse(
                plan_id=plan_id,
                overall_eligible=True,
                evaluation_date=datetime.utcnow(),
                total_rules_evaluated=0,
                passed_rules=0,
                failed_rules=0,
                override_count=0,
                rule_results=[],
                blocking_issues=[],
                warnings=[]
            )
        
        rule_results = []
        passed_count = 0
        failed_count = 0
        override_count = 0
        blocking_issues = []
        warnings = []
        
        # Evaluate each rule
        for rule in effective_rules:
            try:
                evaluation = rule.evaluate(evaluation_request.applicant_data)
                
                # Convert to schema
                rule_result = RuleEvaluationResult(
                    rule_id=rule.id,
                    rule_name=rule.rule_name,
                    rule_category=RuleCategory(rule.rule_category),
                    rule_type=RuleType(rule.rule_type),
                    rule_severity=RuleSeverity(rule.rule_severity),
                    passed=evaluation['passed'],
                    message=evaluation.get('message'),
                    recommendation=rule.recommendation,
                    exception_applied=evaluation.get('exception_applied', False),
                    can_override=rule.can_override,
                    error=evaluation.get('error')
                )
                
                rule_results.append(rule_result)
                
                if rule_result.passed:
                    passed_count += 1
                else:
                    failed_count += 1
                    
                    # Check for override
                    if (rule.can_override and 
                        evaluation_request.override_codes and 
                        any(code in rule.override_codes for code in evaluation_request.override_codes)):
                        override_count += 1
                        rule_result.passed = True  # Override applied
                    else:
                        # Categorize failures
                        if rule.rule_severity in [RuleSeverity.CRITICAL.value, RuleSeverity.HIGH.value]:
                            blocking_issues.append(rule_result)
                        elif rule.rule_type == RuleType.WARNING.value:
                            warnings.append(rule_result)
                
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.id}: {str(e)}")
                rule_result = RuleEvaluationResult(
                    rule_id=rule.id,
                    rule_name=rule.rule_name,
                    rule_category=RuleCategory(rule.rule_category),
                    rule_type=RuleType(rule.rule_type),
                    rule_severity=RuleSeverity(rule.rule_severity),
                    passed=False,
                    error=str(e),
                    can_override=rule.can_override
                )
                rule_results.append(rule_result)
                failed_count += 1
                blocking_issues.append(rule_result)
        
        # Determine overall eligibility
        overall_eligible = len(blocking_issues) == 0
        
        return EligibilityEvaluationResponse(
            plan_id=plan_id,
            overall_eligible=overall_eligible,
            evaluation_date=datetime.utcnow(),
            total_rules_evaluated=len(effective_rules),
            passed_rules=passed_count,
            failed_rules=failed_count,
            override_count=override_count,
            rule_results=rule_results,
            blocking_issues=blocking_issues,
            warnings=warnings
        )
    
    def get_eligibility_rule_summary(self, plan_id: UUID) -> EligibilityRuleSummary:
        """Get eligibility rule summary for a plan"""
        summary_data = self.repository.get_rule_summary(plan_id)
        
        return EligibilityRuleSummary(
            plan_id=UUID(summary_data['plan_id']),
            total_rules=summary_data['total_rules'],
            active_rules=summary_data['active_rules'],
            mandatory_rules=summary_data['mandatory_rules'],
            by_category=summary_data['by_category'],
            by_type=summary_data['by_type'],
            by_severity=summary_data['by_severity'],
            overridable_rules=summary_data['overridable_rules']
        )
    
    def validate_rule_hierarchy(self, plan_id: UUID) -> Dict[str, Any]:
        """Validate rule hierarchy and dependencies"""
        rules = self.repository.get_by_plan(plan_id)
        
        issues = []
        hierarchy_map = {}
        
        # Build hierarchy map
        for rule in rules:
            if rule.parent_rule_id:
                parent = next((r for r in rules if r.id == rule.parent_rule_id), None)
                if not parent:
                    issues.append({
                        'rule_id': str(rule.id),
                        'rule_name': rule.rule_name,
                        'issue': 'Parent rule not found',
                        'severity': 'error'
                    })
                else:
                    hierarchy_map.setdefault(str(parent.id), []).append(rule)
        
        # Check for circular dependencies
        for rule in rules:
            if self._has_circular_dependency(rule, rules):
                issues.append({
                    'rule_id': str(rule.id),
                    'rule_name': rule.rule_name,
                    'issue': 'Circular dependency detected',
                    'severity': 'error'
                })
        
        return {
            'plan_id': str(plan_id),
            'valid_hierarchy': len([i for i in issues if i['severity'] == 'error']) == 0,
            'issues': issues,
            'hierarchy_depth': self._calculate_hierarchy_depth(hierarchy_map),
            'total_rules': len(rules)
        }
    
    def _has_circular_dependency(self, rule, all_rules, visited=None):
        """Check for circular dependencies in rule hierarchy"""
        if visited is None:
            visited = set()
        
        if rule.id in visited:
            return True
        
        visited.add(rule.id)
        
        if rule.parent_rule_id:
            parent = next((r for r in all_rules if r.id == rule.parent_rule_id), None)
            if parent:
                return self._has_circular_dependency(parent, all_rules, visited.copy())
        
        return False
    
    def _calculate_hierarchy_depth(self, hierarchy_map):
        """Calculate maximum hierarchy depth"""
        def get_depth(rule_id, depth=0):
            children = hierarchy_map.get(rule_id, [])
            if not children:
                return depth
            return max(get_depth(str(child.id), depth + 1) for child in children)
        
        max_depth = 0
        for root_id in hierarchy_map:
            max_depth = max(max_depth, get_depth(root_id))
        
        return max_depth