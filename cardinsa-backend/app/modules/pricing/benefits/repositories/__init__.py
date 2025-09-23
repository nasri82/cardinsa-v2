"""
app/modules/benefits/repositories/__init__.py

Repository Factory for Benefits & Coverage Module
"""

from sqlalchemy.orm import Session
from .benefit_category_repository import BenefitCategoryRepository
from .benefit_type_repository import BenefitTypeRepository
from .coverage_repository import CoverageRepository
from .coverage_option_repository import CoverageOptionRepository
from .benefit_limit_repository import BenefitLimitRepository
from .benefit_calculation_rule_repository import BenefitCalculationRuleRepository
from .plan_benefit_schedule_repository import PlanBenefitScheduleRepository
from .benefit_translation_repository import BenefitTranslationRepository
from .benefit_preapproval_rule_repository import BenefitPreapprovalRuleRepository
from .benefit_condition_repository import BenefitConditionRepository


class BenefitsRepositoryFactory:
    """Factory for creating benefit repositories"""
    
    def __init__(self, db: Session):
        self.db = db
        self._repositories = {}
    
    def get_benefit_category_repository(self) -> BenefitCategoryRepository:
        if 'benefit_category' not in self._repositories:
            self._repositories['benefit_category'] = BenefitCategoryRepository(self.db)
        return self._repositories['benefit_category']
    
    def get_benefit_type_repository(self) -> BenefitTypeRepository:
        if 'benefit_type' not in self._repositories:
            self._repositories['benefit_type'] = BenefitTypeRepository(self.db)
        return self._repositories['benefit_type']
    
    def get_coverage_repository(self) -> CoverageRepository:
        if 'coverage' not in self._repositories:
            self._repositories['coverage'] = CoverageRepository(self.db)
        return self._repositories['coverage']
    
    def get_coverage_option_repository(self) -> CoverageOptionRepository:
        if 'coverage_option' not in self._repositories:
            self._repositories['coverage_option'] = CoverageOptionRepository(self.db)
        return self._repositories['coverage_option']
    
    def get_benefit_limit_repository(self) -> BenefitLimitRepository:
        if 'benefit_limit' not in self._repositories:
            self._repositories['benefit_limit'] = BenefitLimitRepository(self.db)
        return self._repositories['benefit_limit']
    
    def get_benefit_calculation_rule_repository(self) -> BenefitCalculationRuleRepository:
        if 'calculation_rule' not in self._repositories:
            self._repositories['calculation_rule'] = BenefitCalculationRuleRepository(self.db)
        return self._repositories['calculation_rule']
    
    def get_plan_benefit_schedule_repository(self) -> PlanBenefitScheduleRepository:
        if 'benefit_schedule' not in self._repositories:
            self._repositories['benefit_schedule'] = PlanBenefitScheduleRepository(self.db)
        return self._repositories['benefit_schedule']
    
    def get_benefit_translation_repository(self) -> BenefitTranslationRepository:
        if 'translation' not in self._repositories:
            self._repositories['translation'] = BenefitTranslationRepository(self.db)
        return self._repositories['translation']
    
    def get_benefit_preapproval_rule_repository(self) -> BenefitPreapprovalRuleRepository:
        if 'preapproval_rule' not in self._repositories:
            self._repositories['preapproval_rule'] = BenefitPreapprovalRuleRepository(self.db)
        return self._repositories['preapproval_rule']
    
    def get_benefit_condition_repository(self) -> BenefitConditionRepository:
        if 'condition' not in self._repositories:
            self._repositories['condition'] = BenefitConditionRepository(self.db)
        return self._repositories['condition']


# Export all repositories
__all__ = [
    'BenefitCategoryRepository',
    'BenefitTypeRepository', 
    'CoverageRepository',
    'CoverageOptionRepository',
    'BenefitLimitRepository',
    'BenefitCalculationRuleRepository',
    'PlanBenefitScheduleRepository',
    'BenefitTranslationRepository',
    'BenefitPreapprovalRuleRepository',
    'BenefitConditionRepository',
    'BenefitsRepositoryFactory'
]