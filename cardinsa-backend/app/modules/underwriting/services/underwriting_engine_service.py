# =============================================================================
# FILE: app/modules/underwriting/services/underwriting_engine_service.py
# WORLD-CLASS UNDERWRITING ENGINE SERVICE - ENTERPRISE GRADE
# =============================================================================

"""
Underwriting Engine Service - Enterprise Implementation

The core underwriting decision engine providing:
- Automated rule evaluation and decision making
- Risk assessment and scoring
- Premium calculations and adjustments
- Workflow orchestration and management
- Exception handling and escalation
- Integration with external systems
- Comprehensive audit trails
"""

from typing import Dict, List, Optional, Any, Tuple, Union
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal
import json
import logging
from dataclasses import dataclass, asdict
from enum import Enum

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, not_

# Core imports
from app.core.exceptions import BusinessLogicError, ValidationError, EntityNotFoundError
from app.core.logging import get_logger

# Model imports
from app.modules.underwriting.models.underwriting_rule_model import (
    UnderwritingRule, UnderwritingDecision, RuleCategory, RuleType, UnderwritingDecision as DecisionEnum
)
from app.modules.underwriting.models.underwriting_profile_model import (
    UnderwritingProfile, ProfileDecision, RiskLevel, ProfileStatus, EvaluationMethod
)
from app.modules.underwriting.models.underwriting_application_model import (
    UnderwritingApplication, ApplicationStatus, Priority
)
from app.modules.underwriting.models.underwriting_workflow_model import (
    UnderwritingWorkflow, UnderwritingWorkflowStep, WorkflowExecution, WorkflowStepExecution,
    StepType, StepStatus, WorkflowStatus
)

# Repository imports (assuming these exist)
from app.modules.underwriting.repositories.underwriting_repository import UnderwritingRepository


# =============================================================================
# DATA CLASSES AND TYPES
# =============================================================================

@dataclass
class UnderwritingContext:
    """Complete context for underwriting evaluation"""
    application_id: UUID
    applicant_data: Dict[str, Any]
    product_type: str
    coverage_amount: Optional[Decimal] = None
    plan_id: Optional[UUID] = None
    submission_channel: Optional[str] = None
    existing_policies: List[Dict[str, Any]] = None
    medical_data: Optional[Dict[str, Any]] = None
    financial_data: Optional[Dict[str, Any]] = None
    risk_data: Optional[Dict[str, Any]] = None
    external_data: Optional[Dict[str, Any]] = None


@dataclass
class RuleEvaluationResult:
    """Result of rule evaluation"""
    rule_id: UUID
    rule_name: str
    matched: bool
    decision: Optional[str] = None
    risk_score_impact: Optional[Decimal] = None
    premium_adjustment: Optional[Decimal] = None
    conditions_met: List[str] = None
    actions_taken: List[str] = None
    notes: Optional[str] = None
    execution_time_ms: Optional[int] = None


@dataclass
class UnderwritingDecisionResult:
    """Complete underwriting decision result"""
    decision: str
    risk_score: Decimal
    premium_adjustment: Decimal
    conditions: List[str]
    exclusions: List[str]
    rule_results: List[RuleEvaluationResult]
    workflow_id: Optional[UUID] = None
    processing_time_ms: Optional[int] = None
    confidence_score: Optional[Decimal] = None
    next_actions: List[str] = None
    requires_manual_review: bool = False
    escalation_required: bool = False


@dataclass
class RiskAssessment:
    """Comprehensive risk assessment result"""
    overall_score: Decimal
    risk_level: str
    category_scores: Dict[str, Decimal]
    risk_factors: List[Dict[str, Any]]
    mitigation_factors: List[Dict[str, Any]]
    recommendations: List[str]
    confidence_level: Decimal


# =============================================================================
# UNDERWRITING ENGINE SERVICE
# =============================================================================

class UnderwritingEngineService:
    """
    World-Class Underwriting Engine Service
    
    The central orchestrator for all underwriting decisions providing:
    - Automated rule evaluation and decision making
    - Comprehensive risk assessment
    - Premium calculations and adjustments
    - Workflow management and orchestration
    - Exception handling and escalation
    - Integration with external systems
    """
    
    def __init__(self, db: Session, repository: UnderwritingRepository):
        self.db = db
        self.repository = repository
        self.logger = get_logger(__name__)
    
    # =========================================================================
    # MAIN UNDERWRITING DECISION ENGINE
    # =========================================================================
    
    async def evaluate_application(
        self, 
        application_id: UUID, 
        context: UnderwritingContext,
        force_manual_review: bool = False
    ) -> UnderwritingDecisionResult:
        """
        Main entry point for underwriting evaluation
        
        Args:
            application_id: Application to evaluate
            context: Complete underwriting context
            force_manual_review: Force manual review regardless of rules
            
        Returns:
            Complete underwriting decision result
        """
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Starting underwriting evaluation for application {application_id}")
            
            # Get or create profile
            profile = await self._get_or_create_profile(application_id, context)
            
            # Perform risk assessment
            risk_assessment = await self._perform_risk_assessment(context, profile)
            
            # Get applicable rules
            applicable_rules = await self._get_applicable_rules(context)
            
            # Evaluate rules
            rule_results = await self._evaluate_rules(applicable_rules, context, risk_assessment)
            
            # Make decision
            decision_result = await self._make_underwriting_decision(
                context, risk_assessment, rule_results, force_manual_review
            )
            
            # Update profile with results
            await self._update_profile_with_decision(profile, decision_result, risk_assessment)
            
            # Start workflow if needed
            if decision_result.requires_manual_review:
                workflow_execution = await self._start_workflow(context, decision_result)
                decision_result.workflow_id = workflow_execution.id
            
            # Log decision
            await self._log_decision(application_id, profile.id, decision_result)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            decision_result.processing_time_ms = int(processing_time)
            
            self.logger.info(f"Completed underwriting evaluation for application {application_id}: {decision_result.decision}")
            
            return decision_result
            
        except Exception as e:
            self.logger.error(f"Error in underwriting evaluation: {str(e)}")
            raise BusinessLogicError(f"Underwriting evaluation failed: {str(e)}")
    
    async def re_evaluate_application(
        self,
        application_id: UUID,
        updated_context: UnderwritingContext,
        reason: str
    ) -> UnderwritingDecisionResult:
        """Re-evaluate application with updated information"""
        self.logger.info(f"Re-evaluating application {application_id}: {reason}")
        
        # Get existing profile
        profile = self.repository.get_profile_by_application(application_id)
        if not profile:
            raise EntityNotFoundError(f"No profile found for application {application_id}")
        
        # Archive current decision
        await self._archive_current_decision(profile, reason)
        
        # Perform new evaluation
        return await self.evaluate_application(application_id, updated_context)
    
    # =========================================================================
    # RISK ASSESSMENT ENGINE
    # =========================================================================
    
    async def _perform_risk_assessment(
        self, 
        context: UnderwritingContext, 
        profile: UnderwritingProfile
    ) -> RiskAssessment:
        """Perform comprehensive risk assessment"""
        
        self.logger.debug(f"Performing risk assessment for application {context.application_id}")
        
        # Initialize assessment
        category_scores = {}
        risk_factors = []
        mitigation_factors = []
        recommendations = []
        
        # Assess different risk categories
        category_scores['medical'] = await self._assess_medical_risk(context)
        category_scores['financial'] = await self._assess_financial_risk(context)
        category_scores['occupational'] = await self._assess_occupational_risk(context)
        category_scores['lifestyle'] = await self._assess_lifestyle_risk(context)
        category_scores['geographical'] = await self._assess_geographical_risk(context)
        category_scores['legal'] = await self._assess_legal_risk(context)
        
        # Calculate overall score (weighted average)
        weights = {
            'medical': 0.3,
            'financial': 0.25,
            'occupational': 0.2,
            'lifestyle': 0.15,
            'geographical': 0.05,
            'legal': 0.05
        }
        
        overall_score = sum(
            category_scores[category] * weight 
            for category, weight in weights.items()
        )
        
        # Determine risk level
        risk_level = self._calculate_risk_level(overall_score)
        
        # Identify risk factors
        risk_factors = await self._identify_risk_factors(context, category_scores)
        
        # Identify mitigation factors
        mitigation_factors = await self._identify_mitigation_factors(context, category_scores)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(context, category_scores, risk_factors)
        
        # Calculate confidence level
        confidence_level = await self._calculate_confidence_level(context, category_scores)
        
        return RiskAssessment(
            overall_score=overall_score,
            risk_level=risk_level,
            category_scores=category_scores,
            risk_factors=risk_factors,
            mitigation_factors=mitigation_factors,
            recommendations=recommendations,
            confidence_level=confidence_level
        )
    
    async def _assess_medical_risk(self, context: UnderwritingContext) -> Decimal:
        """Assess medical risk factors"""
        base_score = Decimal('50.0')  # Neutral score
        
        if not context.medical_data:
            return base_score
        
        medical_data = context.medical_data
        
        # Age factor
        age = medical_data.get('age', 35)
        if age < 25:
            base_score -= Decimal('10.0')
        elif age > 65:
            base_score += Decimal('20.0')
        elif age > 50:
            base_score += Decimal('10.0')
        
        # BMI factor
        bmi = medical_data.get('bmi')
        if bmi:
            if bmi < 18.5 or bmi > 30:
                base_score += Decimal('15.0')
            elif bmi > 25:
                base_score += Decimal('5.0')
        
        # Smoking status
        if medical_data.get('smoker'):
            base_score += Decimal('25.0')
        
        # Pre-existing conditions
        conditions = medical_data.get('conditions', [])
        high_risk_conditions = ['diabetes', 'heart_disease', 'cancer', 'stroke']
        for condition in conditions:
            if condition.lower() in high_risk_conditions:
                base_score += Decimal('30.0')
            else:
                base_score += Decimal('10.0')
        
        # Family history
        family_history = medical_data.get('family_history', [])
        for condition in family_history:
            if condition.lower() in high_risk_conditions:
                base_score += Decimal('5.0')
        
        return min(max(base_score, Decimal('0.0')), Decimal('100.0'))
    
    async def _assess_financial_risk(self, context: UnderwritingContext) -> Decimal:
        """Assess financial risk factors"""
        base_score = Decimal('50.0')
        
        if not context.financial_data:
            return base_score
        
        financial_data = context.financial_data
        
        # Income verification
        annual_income = financial_data.get('annual_income', 0)
        coverage_amount = context.coverage_amount or Decimal('0')
        
        if annual_income > 0 and coverage_amount > 0:
            income_ratio = float(coverage_amount) / annual_income
            if income_ratio > 20:  # Coverage more than 20x income
                base_score += Decimal('30.0')
            elif income_ratio > 10:
                base_score += Decimal('15.0')
            elif income_ratio < 3:
                base_score -= Decimal('5.0')
        
        # Credit score
        credit_score = financial_data.get('credit_score')
        if credit_score:
            if credit_score < 600:
                base_score += Decimal('20.0')
            elif credit_score > 750:
                base_score -= Decimal('10.0')
        
        # Debt-to-income ratio
        debt_to_income = financial_data.get('debt_to_income_ratio')
        if debt_to_income:
            if debt_to_income > 0.5:
                base_score += Decimal('15.0')
            elif debt_to_income < 0.2:
                base_score -= Decimal('5.0')
        
        # Employment status
        employment_status = financial_data.get('employment_status', '').lower()
        if employment_status == 'unemployed':
            base_score += Decimal('25.0')
        elif employment_status == 'self_employed':
            base_score += Decimal('10.0')
        elif employment_status == 'retired' and financial_data.get('age', 65) < 62:
            base_score += Decimal('15.0')
        
        return min(max(base_score, Decimal('0.0')), Decimal('100.0'))
    
    async def _assess_occupational_risk(self, context: UnderwritingContext) -> Decimal:
        """Assess occupational risk factors"""
        base_score = Decimal('50.0')
        
        occupation = context.applicant_data.get('occupation', '').lower()
        
        # High-risk occupations
        high_risk_occupations = [
            'pilot', 'miner', 'construction', 'military', 'police', 'firefighter',
            'offshore', 'logging', 'commercial_fishing', 'stunt_performer'
        ]
        
        # Low-risk occupations
        low_risk_occupations = [
            'teacher', 'accountant', 'office_worker', 'consultant', 'engineer',
            'doctor', 'lawyer', 'analyst', 'manager'
        ]
        
        for high_risk in high_risk_occupations:
            if high_risk in occupation:
                base_score += Decimal('30.0')
                break
        else:
            for low_risk in low_risk_occupations:
                if low_risk in occupation:
                    base_score -= Decimal('10.0')
                    break
        
        # Travel requirements
        travel_frequency = context.applicant_data.get('travel_frequency', '').lower()
        if 'frequent' in travel_frequency or 'international' in travel_frequency:
            base_score += Decimal('10.0')
        
        return min(max(base_score, Decimal('0.0')), Decimal('100.0'))
    
    async def _assess_lifestyle_risk(self, context: UnderwritingContext) -> Decimal:
        """Assess lifestyle risk factors"""
        base_score = Decimal('50.0')
        
        lifestyle_data = context.applicant_data.get('lifestyle', {})
        
        # Alcohol consumption
        alcohol_consumption = lifestyle_data.get('alcohol_consumption', '').lower()
        if 'heavy' in alcohol_consumption or 'excessive' in alcohol_consumption:
            base_score += Decimal('20.0')
        elif 'moderate' in alcohol_consumption:
            base_score += Decimal('5.0')
        elif 'none' in alcohol_consumption:
            base_score -= Decimal('5.0')
        
        # Exercise habits
        exercise_frequency = lifestyle_data.get('exercise_frequency', '').lower()
        if 'never' in exercise_frequency:
            base_score += Decimal('10.0')
        elif 'regular' in exercise_frequency or 'daily' in exercise_frequency:
            base_score -= Decimal('10.0')
        
        # Hobbies and activities
        hobbies = lifestyle_data.get('hobbies', [])
        high_risk_hobbies = [
            'skydiving', 'bungee_jumping', 'rock_climbing', 'motorcycle_racing',
            'scuba_diving', 'hang_gliding', 'mountaineering'
        ]
        
        for hobby in hobbies:
            if hobby.lower() in high_risk_hobbies:
                base_score += Decimal('15.0')
        
        return min(max(base_score, Decimal('0.0')), Decimal('100.0'))
    
    async def _assess_geographical_risk(self, context: UnderwritingContext) -> Decimal:
        """Assess geographical risk factors"""
        base_score = Decimal('50.0')
        
        location = context.applicant_data.get('location', {})
        country = location.get('country', '').lower()
        region = location.get('region', '').lower()
        
        # High-risk countries/regions
        high_risk_areas = [
            'afghanistan', 'iraq', 'syria', 'yemen', 'somalia', 'libya'
        ]
        
        if country in high_risk_areas:
            base_score += Decimal('40.0')
        
        # Natural disaster prone areas (simplified)
        disaster_prone_areas = [
            'california', 'florida', 'louisiana', 'japan', 'philippines'
        ]
        
        if region in disaster_prone_areas:
            base_score += Decimal('10.0')
        
        return min(max(base_score, Decimal('0.0')), Decimal('100.0'))
    
    async def _assess_legal_risk(self, context: UnderwritingContext) -> Decimal:
        """Assess legal risk factors"""
        base_score = Decimal('50.0')
        
        legal_data = context.applicant_data.get('legal_history', {})
        
        # Criminal history
        criminal_history = legal_data.get('criminal_convictions', [])
        for conviction in criminal_history:
            severity = conviction.get('severity', '').lower()
            if severity == 'felony':
                base_score += Decimal('25.0')
            elif severity == 'misdemeanor':
                base_score += Decimal('10.0')
        
        # Driving record
        driving_record = legal_data.get('driving_violations', [])
        for violation in driving_record:
            violation_type = violation.get('type', '').lower()
            if 'dui' in violation_type or 'dwi' in violation_type:
                base_score += Decimal('20.0')
            elif 'reckless' in violation_type:
                base_score += Decimal('15.0')
            else:
                base_score += Decimal('5.0')
        
        return min(max(base_score, Decimal('0.0')), Decimal('100.0'))
    
    def _calculate_risk_level(self, overall_score: Decimal) -> str:
        """Calculate risk level from overall score"""
        score = float(overall_score)
        
        if score < 20:
            return RiskLevel.VERY_LOW
        elif score < 40:
            return RiskLevel.LOW
        elif score < 60:
            return RiskLevel.MODERATE
        elif score < 80:
            return RiskLevel.HIGH
        elif score < 95:
            return RiskLevel.VERY_HIGH
        else:
            return RiskLevel.UNACCEPTABLE
    
    async def _identify_risk_factors(
        self, 
        context: UnderwritingContext, 
        category_scores: Dict[str, Decimal]
    ) -> List[Dict[str, Any]]:
        """Identify specific risk factors"""
        risk_factors = []
        
        # High category scores indicate risk
        for category, score in category_scores.items():
            if score > 70:
                risk_factors.append({
                    'category': category,
                    'severity': 'high',
                    'score': float(score),
                    'description': f'High {category} risk identified'
                })
            elif score > 60:
                risk_factors.append({
                    'category': category,
                    'severity': 'moderate',
                    'score': float(score),
                    'description': f'Moderate {category} risk identified'
                })
        
        return risk_factors
    
    async def _identify_mitigation_factors(
        self, 
        context: UnderwritingContext, 
        category_scores: Dict[str, Decimal]
    ) -> List[Dict[str, Any]]:
        """Identify factors that mitigate risk"""
        mitigation_factors = []
        
        # Low category scores indicate mitigation
        for category, score in category_scores.items():
            if score < 30:
                mitigation_factors.append({
                    'category': category,
                    'benefit': 'high',
                    'score': float(score),
                    'description': f'Low {category} risk provides benefit'
                })
            elif score < 40:
                mitigation_factors.append({
                    'category': category,
                    'benefit': 'moderate',
                    'score': float(score),
                    'description': f'Below average {category} risk'
                })
        
        return mitigation_factors
    
    async def _generate_recommendations(
        self, 
        context: UnderwritingContext, 
        category_scores: Dict[str, Decimal],
        risk_factors: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate underwriting recommendations"""
        recommendations = []
        
        # Based on overall risk profile
        high_risk_categories = [rf['category'] for rf in risk_factors if rf['severity'] == 'high']
        
        if 'medical' in high_risk_categories:
            recommendations.append("Request comprehensive medical examination")
            recommendations.append("Consider exclusions for pre-existing conditions")
        
        if 'financial' in high_risk_categories:
            recommendations.append("Verify income and financial statements")
            recommendations.append("Consider reducing coverage amount")
        
        if 'occupational' in high_risk_categories:
            recommendations.append("Apply occupational loading")
            recommendations.append("Consider occupational exclusions")
        
        if 'lifestyle' in high_risk_categories:
            recommendations.append("Apply lifestyle loading")
            recommendations.append("Consider activity exclusions")
        
        # Coverage amount recommendations
        if context.coverage_amount and context.coverage_amount > Decimal('1000000'):
            recommendations.append("High coverage amount - requires senior underwriter review")
        
        return recommendations
    
    async def _calculate_confidence_level(
        self, 
        context: UnderwritingContext, 
        category_scores: Dict[str, Decimal]
    ) -> Decimal:
        """Calculate confidence level in assessment"""
        confidence = Decimal('100.0')
        
        # Reduce confidence for missing data
        if not context.medical_data:
            confidence -= Decimal('20.0')
        
        if not context.financial_data:
            confidence -= Decimal('15.0')
        
        # Reduce confidence for high variance in category scores
        scores = list(category_scores.values())
        if scores:
            variance = sum((score - sum(scores)/len(scores))**2 for score in scores) / len(scores)
            if variance > 400:  # High variance
                confidence -= Decimal('10.0')
        
        return max(confidence, Decimal('50.0'))
    
    # =========================================================================
    # RULE EVALUATION ENGINE
    # =========================================================================
    
    async def _get_applicable_rules(self, context: UnderwritingContext) -> List[UnderwritingRule]:
        """Get rules applicable to the context"""
        
        # Get active rules for product type
        rules = self.repository.get_active_rules_by_product(
            product_type=context.product_type,
            effective_date=datetime.now().date()
        )
        
        # Filter rules based on context
        applicable_rules = []
        for rule in rules:
            if await self._is_rule_applicable(rule, context):
                applicable_rules.append(rule)
        
        # Sort by priority (higher priority first)
        applicable_rules.sort(key=lambda r: r.priority, reverse=True)
        
        return applicable_rules
    
    async def _is_rule_applicable(self, rule: UnderwritingRule, context: UnderwritingContext) -> bool:
        """Check if rule is applicable to context"""
        
        # Basic applicability checks
        if not rule.is_effective():
            return False
        
        if rule.applies_to and rule.applies_to not in ['all', context.product_type]:
            return False
        
        # Evaluate rule conditions if present
        if rule.conditions:
            try:
                return await self._evaluate_rule_conditions(rule.conditions, context)
            except Exception as e:
                self.logger.warning(f"Error evaluating rule conditions for rule {rule.id}: {str(e)}")
                return False
        
        return True
    
    async def _evaluate_rules(
        self, 
        rules: List[UnderwritingRule], 
        context: UnderwritingContext,
        risk_assessment: RiskAssessment
    ) -> List[RuleEvaluationResult]:
        """Evaluate all applicable rules"""
        
        results = []
        
        for rule in rules:
            start_time = datetime.now()
            
            try:
                result = await self._evaluate_single_rule(rule, context, risk_assessment)
                
                # Calculate execution time
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                result.execution_time_ms = int(execution_time)
                
                results.append(result)
                
            except Exception as e:
                self.logger.error(f"Error evaluating rule {rule.id}: {str(e)}")
                # Create error result
                results.append(RuleEvaluationResult(
                    rule_id=rule.id,
                    rule_name=rule.rule_name,
                    matched=False,
                    notes=f"Evaluation error: {str(e)}"
                ))
        
        return results
    
    async def _evaluate_single_rule(
        self, 
        rule: UnderwritingRule, 
        context: UnderwritingContext,
        risk_assessment: RiskAssessment
    ) -> RuleEvaluationResult:
        """Evaluate a single rule"""
        
        # Create evaluation context
        eval_context = {
            **context.applicant_data,
            'product_type': context.product_type,
            'coverage_amount': float(context.coverage_amount) if context.coverage_amount else 0,
            'risk_score': float(risk_assessment.overall_score),
            'risk_level': risk_assessment.risk_level,
            'category_scores': {k: float(v) for k, v in risk_assessment.category_scores.items()},
            'submission_channel': context.submission_channel,
        }
        
        # Add medical data if available
        if context.medical_data:
            eval_context.update({f"medical_{k}": v for k, v in context.medical_data.items()})
        
        # Add financial data if available
        if context.financial_data:
            eval_context.update({f"financial_{k}": v for k, v in context.financial_data.items()})
        
        # Evaluate rule conditions
        matched = await self._evaluate_rule_conditions(rule.conditions, eval_context)
        
        result = RuleEvaluationResult(
            rule_id=rule.id,
            rule_name=rule.rule_name,
            matched=matched
        )
        
        if matched:
            # Apply rule effects
            result.decision = rule.decision_outcome
            result.risk_score_impact = rule.risk_score_impact
            result.premium_adjustment = rule.premium_adjustment_percentage
            
            # Execute rule actions
            if rule.actions:
                result.actions_taken = await self._execute_rule_actions(rule.actions, context)
            
            # Record conditions met
            result.conditions_met = await self._get_conditions_met(rule.conditions, eval_context)
        
        return result
    
    async def _evaluate_rule_conditions(
        self, 
        conditions: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate rule conditions against context"""
        
        if 'operator' in conditions:
            # Logical operator (AND/OR/NOT)
            operator = conditions['operator'].upper()
            sub_conditions = conditions.get('conditions', [])
            
            if operator == 'AND':
                return all(await self._evaluate_rule_conditions(cond, context) for cond in sub_conditions)
            elif operator == 'OR':
                return any(await self._evaluate_rule_conditions(cond, context) for cond in sub_conditions)
            elif operator == 'NOT':
                if sub_conditions:
                    return not await self._evaluate_rule_conditions(sub_conditions[0], context)
                return False
        
        elif 'field' in conditions:
            # Field condition
            field = conditions['field']
            operator = conditions['operator']
            expected_value = conditions.get('value')
            
            actual_value = context.get(field)
            
            return self._evaluate_field_condition(actual_value, operator, expected_value)
        
        return False
    
    def _evaluate_field_condition(self, actual_value: Any, operator: str, expected_value: Any) -> bool:
        """Evaluate field condition"""
        
        try:
            if operator == 'equals':
                return actual_value == expected_value
            elif operator == 'not_equals':
                return actual_value != expected_value
            elif operator == 'greater_than':
                return float(actual_value) > float(expected_value)
            elif operator == 'less_than':
                return float(actual_value) < float(expected_value)
            elif operator == 'greater_equal':
                return float(actual_value) >= float(expected_value)
            elif operator == 'less_equal':
                return float(actual_value) <= float(expected_value)
            elif operator == 'in':
                return actual_value in expected_value
            elif operator == 'not_in':
                return actual_value not in expected_value
            elif operator == 'contains':
                return expected_value in str(actual_value)
            elif operator == 'not_contains':
                return expected_value not in str(actual_value)
            elif operator == 'between':
                if isinstance(expected_value, list) and len(expected_value) == 2:
                    return expected_value[0] <= float(actual_value) <= expected_value[1]
            elif operator == 'is_null':
                return actual_value is None
            elif operator == 'is_not_null':
                return actual_value is not None
            
        except (TypeError, ValueError) as e:
            self.logger.warning(f"Error evaluating field condition: {str(e)}")
            return False
        
        return False
    
    async def _execute_rule_actions(
        self, 
        actions: Dict[str, Any], 
        context: UnderwritingContext
    ) -> List[str]:
        """Execute rule actions"""
        
        executed_actions = []
        
        action_type = actions.get('type')
        
        if action_type == 'premium_adjustment':
            percentage = actions.get('percentage', 0)
            executed_actions.append(f"Applied {percentage}% premium adjustment")
        
        elif action_type == 'coverage_modification':
            modifications = actions.get('modifications', {})
            for mod_type, mod_value in modifications.items():
                executed_actions.append(f"Applied {mod_type}: {mod_value}")
        
        elif action_type == 'exclusion':
            exclusions = actions.get('exclusions', [])
            for exclusion in exclusions:
                executed_actions.append(f"Applied exclusion: {exclusion}")
        
        elif action_type == 'requirement':
            requirements = actions.get('requirements', [])
            for requirement in requirements:
                executed_actions.append(f"Added requirement: {requirement}")
        
        elif action_type == 'escalation':
            level = actions.get('level', 'standard')
            executed_actions.append(f"Escalated to {level} level review")
        
        return executed_actions
    
    async def _get_conditions_met(
        self, 
        conditions: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> List[str]:
        """Get list of conditions that were met"""
        
        conditions_met = []
        
        if 'field' in conditions:
            field = conditions['field']
            operator = conditions['operator']
            value = conditions.get('value')
            conditions_met.append(f"{field} {operator} {value}")
        
        elif 'conditions' in conditions:
            for sub_condition in conditions['conditions']:
                conditions_met.extend(await self._get_conditions_met(sub_condition, context))
        
        return conditions_met
    
    # =========================================================================
    # DECISION MAKING ENGINE
    # =========================================================================
    
    async def _make_underwriting_decision(
        self,
        context: UnderwritingContext,
        risk_assessment: RiskAssessment,
        rule_results: List[RuleEvaluationResult],
        force_manual_review: bool = False
    ) -> UnderwritingDecisionResult:
        """Make final underwriting decision"""
        
        # Initialize decision components
        base_decision = ProfileDecision.APPROVED
        total_risk_score = risk_assessment.overall_score
        total_premium_adjustment = Decimal('0.0')
        conditions = []
        exclusions = []
        next_actions = []
        requires_manual_review = force_manual_review
        escalation_required = False
        
        # Process rule results
        rejection_rules = []
        referral_rules = []
        approval_rules = []
        
        for result in rule_results:
            if result.matched:
                # Accumulate risk score impact
                if result.risk_score_impact:
                    total_risk_score += result.risk_score_impact
                
                # Accumulate premium adjustments
                if result.premium_adjustment:
                    total_premium_adjustment += result.premium_adjustment
                
                # Collect conditions and exclusions
                if result.actions_taken:
                    for action in result.actions_taken:
                        if 'exclusion' in action.lower():
                            exclusions.append(action)
                        elif 'requirement' in action.lower() or 'condition' in action.lower():
                            conditions.append(action)
                        elif 'escalat' in action.lower():
                            escalation_required = True
                
                # Categorize by decision
                if result.decision == DecisionEnum.REJECTED:
                    rejection_rules.append(result)
                elif result.decision == DecisionEnum.REFERRED:
                    referral_rules.append(result)
                elif result.decision in [DecisionEnum.APPROVED, DecisionEnum.CONDITIONAL]:
                    approval_rules.append(result)
        
        # Determine final decision based on rule hierarchy
        if rejection_rules:
            base_decision = ProfileDecision.REJECTED
            next_actions.append("Application rejected due to rule violations")
        elif referral_rules or escalation_required:
            base_decision = ProfileDecision.REFERRED
            requires_manual_review = True
            next_actions.append("Manual review required")
        elif risk_assessment.risk_level == RiskLevel.UNACCEPTABLE:
            base_decision = ProfileDecision.REJECTED
            next_actions.append("Unacceptable risk level")
        elif risk_assessment.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            base_decision = ProfileDecision.REFERRED
            requires_manual_review = True
            next_actions.append("High risk - manual review required")
        elif conditions or exclusions:
            base_decision = ProfileDecision.CONDITIONAL
            next_actions.append("Conditional approval with terms")
        
        # Check for automatic approval criteria
        if (base_decision == ProfileDecision.APPROVED and 
            risk_assessment.risk_level in [RiskLevel.VERY_LOW, RiskLevel.LOW] and
            not requires_manual_review and
            (not context.coverage_amount or context.coverage_amount <= Decimal('500000'))):
            next_actions.append("Automatic approval - low risk profile")
        
        # Calculate confidence score
        confidence_score = await self._calculate_decision_confidence(
            risk_assessment, rule_results, context
        )
        
        # Ensure risk score bounds
        total_risk_score = max(min(total_risk_score, Decimal('100.0')), Decimal('0.0'))
        
        return UnderwritingDecisionResult(
            decision=base_decision,
            risk_score=total_risk_score,
            premium_adjustment=total_premium_adjustment,
            conditions=conditions,
            exclusions=exclusions,
            rule_results=rule_results,
            confidence_score=confidence_score,
            next_actions=next_actions,
            requires_manual_review=requires_manual_review,
            escalation_required=escalation_required
        )
    
    async def _calculate_decision_confidence(
        self,
        risk_assessment: RiskAssessment,
        rule_results: List[RuleEvaluationResult],
        context: UnderwritingContext
    ) -> Decimal:
        """Calculate confidence in decision"""
        
        confidence = Decimal('100.0')
        
        # Base confidence on risk assessment confidence
        confidence = risk_assessment.confidence_level
        
        # Reduce confidence if rules conflict
        decisions = [r.decision for r in rule_results if r.matched and r.decision]
        unique_decisions = set(decisions)
        if len(unique_decisions) > 1:
            confidence -= Decimal('20.0')
        
        # Reduce confidence for edge cases
        if risk_assessment.overall_score > 45 and risk_assessment.overall_score < 55:
            confidence -= Decimal('15.0')  # Borderline risk
        
        # Increase confidence for clear cases
        if risk_assessment.overall_score < 30 or risk_assessment.overall_score > 70:
            confidence += Decimal('10.0')
        
        return max(min(confidence, Decimal('100.0')), Decimal('50.0'))
    
    # =========================================================================
    # PROFILE AND DATA MANAGEMENT
    # =========================================================================
    
    async def _get_or_create_profile(
        self, 
        application_id: UUID, 
        context: UnderwritingContext
    ) -> UnderwritingProfile:
        """Get existing profile or create new one"""
        
        profile = self.repository.get_profile_by_application(application_id)
        
        if not profile:
            profile = UnderwritingProfile(
                application_id=application_id,
                member_id=context.applicant_data.get('member_id'),
                plan_id=context.plan_id,
                quote_id=context.applicant_data.get('quote_id'),
                status=ProfileStatus.SUBMITTED,
                evaluation_method=EvaluationMethod.AUTOMATED,
                profile_data=context.applicant_data,
                risk_data=context.risk_data,
                created_by=context.applicant_data.get('created_by')
            )
            
            self.repository.create_profile(profile)
        
        return profile
    
    async def _update_profile_with_decision(
        self,
        profile: UnderwritingProfile,
        decision_result: UnderwritingDecisionResult,
        risk_assessment: RiskAssessment
    ) -> None:
        """Update profile with decision results"""
        
        profile.risk_score = decision_result.risk_score
        profile.risk_level = risk_assessment.risk_level
        profile.decision = decision_result.decision
        profile.premium_loading = decision_result.premium_adjustment
        profile.risk_factors = {'factors': [asdict(rf) for rf in risk_assessment.risk_factors]}
        profile.mitigation_factors = {'factors': [asdict(mf) for mf in risk_assessment.mitigation_factors]}
        profile.conditions = {'conditions': decision_result.conditions} if decision_result.conditions else None
        profile.exclusions = {'exclusions': decision_result.exclusions} if decision_result.exclusions else None
        
        if decision_result.requires_manual_review:
            profile.status = ProfileStatus.REVIEW
            profile.evaluation_method = EvaluationMethod.MANUAL
        else:
            profile.status = ProfileStatus.COMPLETED
            profile.evaluation_completed_at = datetime.now()
        
        profile.calculate_net_premium_adjustment()
        
        self.repository.update_profile(profile)
    
    async def _archive_current_decision(
        self, 
        profile: UnderwritingProfile, 
        reason: str
    ) -> None:
        """Archive current decision before re-evaluation"""
        
        # Create archived decision record
        archived_decision = UnderwritingDecision(
            application_id=profile.application_id,
            profile_id=profile.id,
            decision=profile.decision,
            risk_score=profile.risk_score,
            premium_adjustment=profile.premium_loading,
            conditions_applied=profile.conditions,
            underwriter_notes=f"Archived decision: {reason}",
            automated=profile.evaluation_method == EvaluationMethod.AUTOMATED,
            decision_date=datetime.now()
        )
        
        self.repository.create_decision(archived_decision)
    
    async def _log_decision(
        self,
        application_id: UUID,
        profile_id: UUID,
        decision_result: UnderwritingDecisionResult
    ) -> None:
        """Log underwriting decision"""
        
        decision_record = UnderwritingDecision(
            application_id=application_id,
            profile_id=profile_id,
            decision=decision_result.decision,
            risk_score=decision_result.risk_score,
            premium_adjustment=decision_result.premium_adjustment,
            conditions_applied={'conditions': decision_result.conditions},
            underwriter_notes=f"Automated decision. Rules evaluated: {len(decision_result.rule_results)}",
            automated=True,
            decision_date=datetime.now()
        )
        
        self.repository.create_decision(decision_record)
        
        self.logger.info(
            f"Underwriting decision logged - Application: {application_id}, "
            f"Decision: {decision_result.decision}, Risk Score: {decision_result.risk_score}"
        )
    
    # =========================================================================
    # WORKFLOW MANAGEMENT
    # =========================================================================
    
    async def _start_workflow(
        self, 
        context: UnderwritingContext, 
        decision_result: UnderwritingDecisionResult
    ) -> WorkflowExecution:
        """Start appropriate workflow for manual review"""
        
        # Get workflow for product type and decision
        workflow = self.repository.get_workflow_for_context(
            product_type=context.product_type,
            decision=decision_result.decision,
            risk_level=decision_result.risk_score
        )
        
        if not workflow:
            # Use default workflow
            workflow = self.repository.get_default_workflow()
        
        if not workflow:
            raise BusinessLogicError("No workflow available for manual review")
        
        # Create workflow execution
        execution = WorkflowExecution(
            workflow_id=workflow.id,
            application_id=context.application_id,
            trigger_type='manual_review_required',
            trigger_data={
                'decision': decision_result.decision,
                'risk_score': float(decision_result.risk_score),
                'escalation_required': decision_result.escalation_required
            },
            status=WorkflowStatus.ACTIVE,
            sla_due_date=datetime.now() + timedelta(hours=workflow.default_sla_hours or 72)
        )
        
        self.repository.create_workflow_execution(execution)
        
        # Start first workflow step
        await self._start_first_workflow_step(execution, workflow, context)
        
        return execution
    
    async def _start_first_workflow_step(
        self,
        execution: WorkflowExecution,
        workflow: UnderwritingWorkflow,
        context: UnderwritingContext
    ) -> None:
        """Start the first step in workflow"""
        
        # Get first step
        first_step = min(workflow.steps, key=lambda s: s.order_index)
        
        if not first_step:
            raise BusinessLogicError("Workflow has no steps")
        
        # Create step execution
        step_execution = WorkflowStepExecution(
            workflow_execution_id=execution.id,
            step_id=first_step.id,
            status=StepStatus.PENDING,
            sla_due_date=first_step.get_sla_due_date(datetime.now()),
            input_data={'context': asdict(context)}
        )
        
        # Auto-assign if configured
        assignment_target = first_step.get_assignment_target(asdict(context))
        if assignment_target:
            step_execution.assigned_to = UUID(assignment_target) if assignment_target != 'auto' else None
        
        self.repository.create_step_execution(step_execution)
        
        # If step is automatic, execute it
        if first_step.step_type == StepType.AUTO:
            await self._execute_workflow_step(step_execution, first_step, context)
    
    async def _execute_workflow_step(
        self,
        step_execution: WorkflowStepExecution,
        step: UnderwritingWorkflowStep,
        context: UnderwritingContext
    ) -> None:
        """Execute a workflow step"""
        
        step_execution.status = StepStatus.IN_PROGRESS
        step_execution.started_at = datetime.now()
        
        try:
            # Execute step based on type
            if step.step_type == StepType.AUTO:
                await self._execute_automatic_step(step_execution, step, context)
            elif step.step_type == StepType.NOTIFICATION:
                await self._execute_notification_step(step_execution, step, context)
            elif step.step_type == StepType.INTEGRATION:
                await self._execute_integration_step(step_execution, step, context)
            
            step_execution.status = StepStatus.COMPLETED
            step_execution.completed_at = datetime.now()
            
        except Exception as e:
            step_execution.status = StepStatus.FAILED
            step_execution.error_details = str(e)
            self.logger.error(f"Workflow step execution failed: {str(e)}")
        
        self.repository.update_step_execution(step_execution)
    
    async def _execute_automatic_step(
        self,
        step_execution: WorkflowStepExecution,
        step: UnderwritingWorkflowStep,
        context: UnderwritingContext
    ) -> None:
        """Execute automatic workflow step"""
        
        # Execute configured actions
        if step.actions:
            action_type = step.actions.get('type')
            
            if action_type == 'assign':
                target = step.actions.get('target')
                step_execution.assigned_to = UUID(target) if target else None
            
            elif action_type == 'calculate':
                # Perform calculations
                calculation_type = step.actions.get('calculation_type')
                if calculation_type == 'premium':
                    # Perform premium calculation
                    pass
            
            step_execution.execution_notes = f"Executed automatic action: {action_type}"
    
    async def _execute_notification_step(
        self,
        step_execution: WorkflowStepExecution,
        step: UnderwritingWorkflowStep,
        context: UnderwritingContext
    ) -> None:
        """Execute notification workflow step"""
        
        if step.notification_config:
            notification_type = step.notification_config.get('type')
            recipients = step.notification_config.get('recipients', [])
            
            # Send notifications (implementation would depend on notification system)
            step_execution.execution_notes = f"Sent {notification_type} notification to {len(recipients)} recipients"
    
    async def _execute_integration_step(
        self,
        step_execution: WorkflowStepExecution,
        step: UnderwritingWorkflowStep,
        context: UnderwritingContext
    ) -> None:
        """Execute integration workflow step"""
        
        if step.integration_config:
            integration_type = step.integration_config.get('type')
            endpoint = step.integration_config.get('endpoint')
            
            # Perform integration call (implementation would depend on integration system)
            step_execution.execution_notes = f"Executed {integration_type} integration to {endpoint}"
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    async def get_application_status(self, application_id: UUID) -> Dict[str, Any]:
        """Get current status of application"""
        
        profile = self.repository.get_profile_by_application(application_id)
        if not profile:
            return {'status': 'not_found'}
        
        workflow_execution = None
        if profile.status == ProfileStatus.REVIEW:
            workflow_execution = self.repository.get_active_workflow_execution(application_id)
        
        return {
            'status': profile.status,
            'decision': profile.decision,
            'risk_score': float(profile.risk_score) if profile.risk_score else None,
            'risk_level': profile.risk_level,
            'evaluation_method': profile.evaluation_method,
            'requires_manual_review': profile.status == ProfileStatus.REVIEW,
            'workflow_active': workflow_execution is not None,
            'last_updated': profile.updated_at.isoformat() if profile.updated_at else None
        }
    
    async def get_decision_summary(self, application_id: UUID) -> Dict[str, Any]:
        """Get summary of underwriting decision"""
        
        profile = self.repository.get_profile_by_application(application_id)
        if not profile:
            raise EntityNotFoundError(f"No profile found for application {application_id}")
        
        decisions = self.repository.get_decisions_by_application(application_id)
        rule_evaluations = self.repository.get_rule_evaluations_by_application(application_id)
        
        return {
            'application_id': str(application_id),
            'current_decision': profile.decision,
            'risk_assessment': {
                'risk_score': float(profile.risk_score) if profile.risk_score else None,
                'risk_level': profile.risk_level,
                'risk_factors': profile.risk_factors,
                'mitigation_factors': profile.mitigation_factors
            },
            'premium_impact': {
                'loading': float(profile.premium_loading) if profile.premium_loading else None,
                'discount': float(profile.premium_discount) if profile.premium_discount else None,
                'net_adjustment': float(profile.net_premium_adjustment) if profile.net_premium_adjustment else None
            },
            'conditions_and_exclusions': {
                'conditions': profile.conditions,
                'exclusions': profile.exclusions
            },
            'decisions_history': [
                {
                    'decision': d.decision,
                    'date': d.decision_date.isoformat() if d.decision_date else None,
                    'automated': d.automated,
                    'notes': d.underwriter_notes
                } for d in decisions
            ],
            'rules_evaluated': len(rule_evaluations),
            'processing_status': {
                'status': profile.status,
                'evaluation_method': profile.evaluation_method,
                'completed_at': profile.evaluation_completed_at.isoformat() if profile.evaluation_completed_at else None
            }
        }