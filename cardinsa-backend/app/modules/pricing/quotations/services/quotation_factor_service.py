# app/modules/insurance/quotations/services/quotation_factor_service.py

from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any, Union
from uuid import UUID
import logging

from ..models import QuotationFactor
from ..schemas import (
    QuotationFactorCreate, QuotationFactorUpdate, QuotationFactorResponse,
    QuotationFactorSummary, QuotationFactorBulkCreate, FactorType,
    QuotationFactorNumericRequest, QuotationFactorBooleanRequest,
    QuotationFactorComplexRequest, QuotationFactorsByType,
    QuotationFactorsGrouped, QuotationFactorImpactAnalysis
)
from ..repositories import QuotationFactorRepository, QuotationRepository
from app.core.exceptions import BusinessLogicError, ValidationError, NotFoundError, ConflictError


logger = logging.getLogger(__name__)


class QuotationFactorService:
    """
    Service class for QuotationFactor business logic
    
    Handles pricing factor operations including creation, validation,
    impact analysis, and business rule enforcement.
    """

    def __init__(self, db: Session):
        self.db = db
        self.factor_repo = QuotationFactorRepository(db)
        self.quotation_repo = QuotationRepository(db)

    # ========== CREATE OPERATIONS ==========

    async def create_factor(self, quotation_id: UUID, key: str, value: Any,
                           factor_type: FactorType = None, impact_description: str = None,
                           created_by: UUID = None) -> QuotationFactorResponse:
        """Create a new quotation factor with business validations"""
        try:
            # Validate quotation exists and can be modified
            await self._validate_quotation_modifiable(quotation_id)
            
            # Validate factor data
            await self._validate_factor_creation(quotation_id, key, value, factor_type)
            
            # Create factor using appropriate method based on value type
            if isinstance(value, (int, float)):
                factor = self.factor_repo.create_numeric_factor(
                    quotation_id, key, float(value), factor_type, impact_description, created_by
                )
            elif isinstance(value, bool):
                factor = self.factor_repo.create_boolean_factor(
                    quotation_id, key, value, factor_type, impact_description, created_by
                )
            elif isinstance(value, (dict, list)):
                factor = self.factor_repo.create_complex_factor(
                    quotation_id, key, value, factor_type, impact_description, created_by
                )
            else:
                # String or other types
                factor_data = QuotationFactorCreate(
                    quotation_id=quotation_id,
                    key=key,
                    value=str(value),
                    factor_type=factor_type,
                    impact_description=impact_description
                )
                factor = self.factor_repo.create_factor(factor_data, created_by)
            
            logger.info(f"Created factor '{key}' for quotation {quotation_id}")
            
            return QuotationFactorResponse.from_orm(factor)
            
        except Exception as e:
            logger.error(f"Error creating quotation factor: {str(e)}")
            raise BusinessLogicError(f"Failed to create quotation factor: {str(e)}")

    async def create_numeric_factor(self, request: QuotationFactorNumericRequest,
                                   quotation_id: UUID, created_by: UUID = None) -> QuotationFactorResponse:
        """Create a numeric factor with validation"""
        try:
            return await self.create_factor(
                quotation_id=quotation_id,
                key=request.key,
                value=request.numeric_value,
                factor_type=request.factor_type,
                impact_description=request.impact_description,
                created_by=created_by
            )
            
        except Exception as e:
            logger.error(f"Error creating numeric factor: {str(e)}")
            raise BusinessLogicError(f"Failed to create numeric factor: {str(e)}")

    async def create_boolean_factor(self, request: QuotationFactorBooleanRequest,
                                   quotation_id: UUID, created_by: UUID = None) -> QuotationFactorResponse:
        """Create a boolean factor with validation"""
        try:
            return await self.create_factor(
                quotation_id=quotation_id,
                key=request.key,
                value=request.boolean_value,
                factor_type=request.factor_type,
                impact_description=request.impact_description,
                created_by=created_by
            )
            
        except Exception as e:
            logger.error(f"Error creating boolean factor: {str(e)}")
            raise BusinessLogicError(f"Failed to create boolean factor: {str(e)}")

    async def create_complex_factor(self, request: QuotationFactorComplexRequest,
                                   quotation_id: UUID, created_by: UUID = None) -> QuotationFactorResponse:
        """Create a complex factor with validation"""
        try:
            return await self.create_factor(
                quotation_id=quotation_id,
                key=request.key,
                value=request.complex_value,
                factor_type=request.factor_type,
                impact_description=request.impact_description,
                created_by=created_by
            )
            
        except Exception as e:
            logger.error(f"Error creating complex factor: {str(e)}")
            raise BusinessLogicError(f"Failed to create complex factor: {str(e)}")

    async def create_bulk_factors(self, bulk_data: QuotationFactorBulkCreate,
                                 created_by: UUID = None) -> List[QuotationFactorResponse]:
        """Create multiple quotation factors in bulk"""
        try:
            # Validate quotation exists and can be modified
            await self._validate_quotation_modifiable(bulk_data.quotation_id)
            
            # Validate all factors data
            for factor_data in bulk_data.factors:
                await self._validate_factor_creation(
                    bulk_data.quotation_id, factor_data.key, factor_data.value, factor_data.factor_type
                )
            
            # Create factors in bulk
            factors = self.factor_repo.create_bulk_factors(bulk_data.factors, created_by)
            
            logger.info(f"Created {len(factors)} factors for quotation {bulk_data.quotation_id}")
            
            return [QuotationFactorResponse.from_orm(factor) for factor in factors]
            
        except Exception as e:
            logger.error(f"Error creating bulk quotation factors: {str(e)}")
            raise BusinessLogicError(f"Failed to create bulk factors: {str(e)}")

    # ========== READ OPERATIONS ==========

    async def get_factor(self, factor_id: UUID) -> Optional[QuotationFactorResponse]:
        """Get quotation factor by ID"""
        try:
            factor = self.factor_repo.get(factor_id)
            if not factor:
                return None
            
            return QuotationFactorResponse.from_orm(factor)
            
        except Exception as e:
            logger.error(f"Error retrieving quotation factor {factor_id}: {str(e)}")
            raise BusinessLogicError(f"Failed to retrieve quotation factor: {str(e)}")

    async def get_factor_by_key(self, quotation_id: UUID, key: str) -> Optional[QuotationFactorResponse]:
        """Get factor by quotation ID and key"""
        try:
            factor = self.factor_repo.get_by_key(quotation_id, key)
            if not factor:
                return None
            
            return QuotationFactorResponse.from_orm(factor)
            
        except Exception as e:
            logger.error(f"Error retrieving factor by key: {str(e)}")
            raise BusinessLogicError(f"Failed to retrieve factor: {str(e)}")

    async def get_quotation_factors(self, quotation_id: UUID, 
                                   active_only: bool = True) -> List[QuotationFactorResponse]:
        """Get all factors for a quotation"""
        try:
            factors = self.factor_repo.get_by_quotation(quotation_id, active_only)
            return [QuotationFactorResponse.from_orm(factor) for factor in factors]
            
        except Exception as e:
            logger.error(f"Error retrieving quotation factors: {str(e)}")
            raise BusinessLogicError(f"Failed to retrieve quotation factors: {str(e)}")

    async def get_factors_by_type(self, quotation_id: UUID, 
                                 factor_type: FactorType) -> List[QuotationFactorResponse]:
        """Get factors by type"""
        try:
            factors = self.factor_repo.get_by_quotation_and_type(quotation_id, factor_type)
            return [QuotationFactorResponse.from_orm(factor) for factor in factors]
            
        except Exception as e:
            logger.error(f"Error retrieving factors by type: {str(e)}")
            raise BusinessLogicError(f"Failed to retrieve factors by type: {str(e)}")

    async def get_numeric_factors(self, quotation_id: UUID) -> List[QuotationFactorResponse]:
        """Get all numeric factors for a quotation"""
        try:
            factors = self.factor_repo.get_numeric_factors(quotation_id)
            return [QuotationFactorResponse.from_orm(factor) for factor in factors]
            
        except Exception as e:
            logger.error(f"Error retrieving numeric factors: {str(e)}")
            raise BusinessLogicError(f"Failed to retrieve numeric factors: {str(e)}")

    async def get_factors_grouped_by_type(self, quotation_id: UUID) -> QuotationFactorsGrouped:
        """Get factors grouped by type"""
        try:
            grouped_factors = self.factor_repo.get_factors_grouped_by_type(quotation_id)
            
            factor_groups = []
            total_factors = 0
            latest_update = None
            
            for factor_type, factors in grouped_factors.items():
                factor_responses = [QuotationFactorResponse.from_orm(factor) for factor in factors]
                
                factor_groups.append(QuotationFactorsByType(
                    factor_type=factor_type,
                    factors=factor_responses,
                    total_count=len(factor_responses)
                ))
                
                total_factors += len(factors)
                
                # Find latest update time
                for factor in factors:
                    if factor.updated_at and (not latest_update or factor.updated_at > latest_update):
                        latest_update = factor.updated_at
            
            return QuotationFactorsGrouped(
                quotation_id=quotation_id,
                factor_groups=factor_groups,
                total_factors=total_factors,
                last_updated=latest_update
            )
            
        except Exception as e:
            logger.error(f"Error retrieving grouped factors: {str(e)}")
            raise BusinessLogicError(f"Failed to retrieve grouped factors: {str(e)}")

    async def search_factors(self, quotation_id: UUID, search_term: str) -> List[QuotationFactorResponse]:
        """Search factors by key, value, or impact description"""
        try:
            factors = self.factor_repo.search_factors(quotation_id, search_term)
            return [QuotationFactorResponse.from_orm(factor) for factor in factors]
            
        except Exception as e:
            logger.error(f"Error searching factors: {str(e)}")
            raise BusinessLogicError(f"Failed to search factors: {str(e)}")

    # ========== UPDATE OPERATIONS ==========

    async def update_factor(self, factor_id: UUID, factor_data: QuotationFactorUpdate,
                           updated_by: UUID = None) -> Optional[QuotationFactorResponse]:
        """Update quotation factor with business validations"""
        try:
            # Validate factor can be updated
            factor = await self._validate_factor_update(factor_id)
            
            # Validate update data
            await self._validate_factor_update_data(factor.quotation_id, factor_data)
            
            # Update factor
            updated_factor = self.factor_repo.update(factor_id, factor_data, updated_by)
            
            logger.info(f"Updated factor {factor_id}")
            
            return QuotationFactorResponse.from_orm(updated_factor) if updated_factor else None
            
        except Exception as e:
            logger.error(f"Error updating quotation factor {factor_id}: {str(e)}")
            raise BusinessLogicError(f"Failed to update quotation factor: {str(e)}")

    async def update_factor_value(self, factor_id: UUID, value: Any,
                                 impact_description: str = None,
                                 updated_by: UUID = None) -> Optional[QuotationFactorResponse]:
        """Update factor value with type-specific handling"""
        try:
            # Validate factor can be updated
            factor = await self._validate_factor_update(factor_id)
            
            # Update factor value
            updated_factor = self.factor_repo.update_factor_value(
                factor_id, value, impact_description, updated_by
            )
            
            logger.info(f"Updated factor value for {factor_id}")
            
            return QuotationFactorResponse.from_orm(updated_factor) if updated_factor else None
            
        except Exception as e:
            logger.error(f"Error updating factor value: {str(e)}")
            raise BusinessLogicError(f"Failed to update factor value: {str(e)}")

    async def upsert_factor(self, quotation_id: UUID, key: str, value: Any,
                           factor_type: FactorType = None, impact_description: str = None,
                           updated_by: UUID = None) -> QuotationFactorResponse:
        """Insert or update factor by key"""
        try:
            # Validate quotation can be modified
            await self._validate_quotation_modifiable(quotation_id)
            
            # Validate factor data
            await self._validate_factor_creation(quotation_id, key, value, factor_type, allow_existing=True)
            
            # Upsert factor
            factor = self.factor_repo.upsert_factor(
                quotation_id, key, value, factor_type, impact_description, updated_by
            )
            
            logger.info(f"Upserted factor '{key}' for quotation {quotation_id}")
            
            return QuotationFactorResponse.from_orm(factor)
            
        except Exception as e:
            logger.error(f"Error upserting factor: {str(e)}")
            raise BusinessLogicError(f"Failed to upsert factor: {str(e)}")

    async def bulk_upsert_factors(self, quotation_id: UUID, factors: Dict[str, Any],
                                 factor_type: FactorType = None,
                                 updated_by: UUID = None) -> List[QuotationFactorResponse]:
        """Bulk upsert factors"""
        try:
            # Validate quotation can be modified
            await self._validate_quotation_modifiable(quotation_id)
            
            # Validate all factors
            for key, value in factors.items():
                await self._validate_factor_creation(quotation_id, key, value, factor_type, allow_existing=True)
            
            # Bulk upsert factors
            upserted_factors = self.factor_repo.bulk_upsert_factors(
                quotation_id, factors, factor_type, updated_by
            )
            
            logger.info(f"Bulk upserted {len(upserted_factors)} factors for quotation {quotation_id}")
            
            return [QuotationFactorResponse.from_orm(factor) for factor in upserted_factors]
            
        except Exception as e:
            logger.error(f"Error bulk upserting factors: {str(e)}")
            raise BusinessLogicError(f"Failed to bulk upsert factors: {str(e)}")

    # ========== DELETE OPERATIONS ==========

    async def delete_factor(self, factor_id: UUID, deleted_by: UUID = None) -> bool:
        """Soft delete quotation factor"""
        try:
            # Validate factor can be deleted
            factor = await self._validate_factor_deletion(factor_id)
            
            # Soft delete factor
            success = self.factor_repo.soft_delete(factor_id, deleted_by)
            
            if success:
                logger.info(f"Deleted factor {factor_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting quotation factor {factor_id}: {str(e)}")
            raise BusinessLogicError(f"Failed to delete quotation factor: {str(e)}")

    async def delete_factor_by_key(self, quotation_id: UUID, key: str) -> bool:
        """Delete factor by key"""
        try:
            # Validate quotation can be modified
            await self._validate_quotation_modifiable(quotation_id)
            
            # Delete factor
            success = self.factor_repo.delete_by_key(quotation_id, key)
            
            if success:
                logger.info(f"Deleted factor '{key}' for quotation {quotation_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting factor by key: {str(e)}")
            raise BusinessLogicError(f"Failed to delete factor by key: {str(e)}")

    async def delete_factors_by_type(self, quotation_id: UUID, factor_type: FactorType,
                                    deleted_by: UUID = None) -> int:
        """Delete all factors of a specific type"""
        try:
            # Validate quotation can be modified
            await self._validate_quotation_modifiable(quotation_id)
            
            # Delete factors by type
            deleted_count = self.factor_repo.delete_by_type(quotation_id, factor_type)
            
            logger.info(f"Deleted {deleted_count} factors of type {factor_type} for quotation {quotation_id}")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting factors by type: {str(e)}")
            raise BusinessLogicError(f"Failed to delete factors by type: {str(e)}")

    # ========== ANALYSIS OPERATIONS ==========

    async def get_factor_impact_analysis(self, quotation_id: UUID) -> List[QuotationFactorImpactAnalysis]:
        """Analyze factor impacts on pricing"""
        try:
            impact_analysis = self.factor_repo.get_factor_impact_analysis(quotation_id)
            
            analysis_results = []
            for analysis in impact_analysis:
                result = QuotationFactorImpactAnalysis(
                    factor_id=analysis['factor_id'],
                    key=analysis['key'],
                    current_value=analysis['value'],
                    factor_type=analysis['factor_type'],
                    impact_description=analysis['impact_description'],
                    impact_amount=None,  # Would be calculated based on premium
                    impact_percentage=analysis.get('impact_percentage'),
                    is_positive_impact=analysis.get('impact_type') == 'loading'
                )
                analysis_results.append(result)
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error analyzing factor impacts: {str(e)}")
            raise BusinessLogicError(f"Failed to analyze factor impacts: {str(e)}")

    async def get_factors_summary(self, quotation_id: UUID) -> Dict[str, Any]:
        """Get summary statistics for quotation factors"""
        try:
            summary = self.factor_repo.get_factors_summary(quotation_id)
            
            # Add business insights
            summary['insights'] = await self._generate_factor_insights(quotation_id, summary)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error retrieving factors summary: {str(e)}")
            raise BusinessLogicError(f"Failed to retrieve factors summary: {str(e)}")

    async def validate_factors(self, quotation_id: UUID) -> Dict[str, Any]:
        """Validate all factors for a quotation"""
        try:
            validation_result = self.factor_repo.validate_factors(quotation_id)
            
            # Add business-specific validations
            business_validations = await self._perform_business_validations(quotation_id)
            
            # Merge validation results
            validation_result['business_validations'] = business_validations
            validation_result['overall_valid'] = (
                validation_result['is_valid'] and 
                business_validations.get('is_valid', True)
            )
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating factors: {str(e)}")
            raise BusinessLogicError(f"Failed to validate factors: {str(e)}")

    # ========== UTILITY OPERATIONS ==========

    async def duplicate_factors_to_quotation(self, source_quotation_id: UUID,
                                            target_quotation_id: UUID,
                                            created_by: UUID = None) -> List[QuotationFactorResponse]:
        """Duplicate factors from one quotation to another"""
        try:
            # Validate both quotations exist
            source_quotation = self.quotation_repo.get(source_quotation_id)
            target_quotation = self.quotation_repo.get(target_quotation_id)
            
            if not source_quotation:
                raise NotFoundError("Source quotation not found")
            if not target_quotation:
                raise NotFoundError("Target quotation not found")
            
            # Validate target quotation can be modified
            await self._validate_quotation_modifiable(target_quotation_id)
            
            # Duplicate factors
            duplicated_factors = self.factor_repo.duplicate_factors_to_quotation(
                source_quotation_id, target_quotation_id, created_by
            )
            
            logger.info(f"Duplicated {len(duplicated_factors)} factors from {source_quotation_id} to {target_quotation_id}")
            
            return [QuotationFactorResponse.from_orm(factor) for factor in duplicated_factors]
            
        except Exception as e:
            logger.error(f"Error duplicating factors: {str(e)}")
            raise BusinessLogicError(f"Failed to duplicate factors: {str(e)}")

    async def recalculate_factor_impacts(self, quotation_id: UUID, base_premium: float) -> List[Dict[str, Any]]:
        """Recalculate factor impacts based on base premium"""
        try:
            factors = self.factor_repo.get_numeric_factors(quotation_id)
            
            recalculated_impacts = []
            for factor in factors:
                if factor.numeric_value:
                    impact_amount = base_premium * (factor.numeric_value - 1)
                    impact_percentage = (factor.numeric_value - 1) * 100
                    
                    recalculated_impacts.append({
                        'factor_id': factor.id,
                        'key': factor.key,
                        'factor_value': factor.numeric_value,
                        'impact_amount': impact_amount,
                        'impact_percentage': impact_percentage,
                        'impact_type': 'loading' if impact_amount > 0 else 'discount' if impact_amount < 0 else 'neutral'
                    })
            
            return recalculated_impacts
            
        except Exception as e:
            logger.error(f"Error recalculating factor impacts: {str(e)}")
            raise BusinessLogicError(f"Failed to recalculate factor impacts: {str(e)}")

    # ========== VALIDATION METHODS ==========

    async def _validate_quotation_modifiable(self, quotation_id: UUID) -> None:
        """Validate quotation exists and can be modified"""
        quotation = self.quotation_repo.get(quotation_id)
        if not quotation:
            raise NotFoundError("Quotation not found")
        
        if quotation.is_locked:
            raise ConflictError("Cannot modify factors in locked quotation")
        
        if quotation.status in ['converted', 'expired']:
            raise ConflictError(f"Cannot modify factors in {quotation.status} quotation")

    async def _validate_factor_creation(self, quotation_id: UUID, key: str, value: Any,
                                       factor_type: FactorType = None, allow_existing: bool = False) -> None:
        """Validate factor creation business rules"""
        # Validate key format
        if not key or not key.strip():
            raise ValidationError("Factor key cannot be empty")
        
        normalized_key = key.lower().strip()
        if not normalized_key.replace('_', '').replace('-', '').isalnum():
            raise ValidationError("Factor key must contain only alphanumeric characters, underscores, and hyphens")
        
        # Check for existing key if not allowing updates
        if not allow_existing and self.factor_repo.factor_exists(quotation_id, normalized_key):
            raise ConflictError(f"Factor with key '{normalized_key}' already exists")
        
        # Validate value based on type
        if isinstance(value, (int, float)):
            if value < 0 and factor_type in ['loading', 'discount']:
                raise ValidationError(f"{factor_type} factor cannot be negative")
        
        # Validate factor type specific rules
        await self._validate_factor_type_rules(factor_type, value)

    async def _validate_factor_update(self, factor_id: UUID) -> QuotationFactor:
        """Validate factor can be updated"""
        factor = self.factor_repo.get(factor_id)
        if not factor:
            raise NotFoundError("Quotation factor not found")
        
        await self._validate_quotation_modifiable(factor.quotation_id)
        
        return factor

    async def _validate_factor_update_data(self, quotation_id: UUID, factor_data: QuotationFactorUpdate) -> None:
        """Validate factor update data"""
        if factor_data.key:
            # Check for duplicate key if changing key
            if self.factor_repo.factor_exists(quotation_id, factor_data.key):
                raise ConflictError(f"Factor with key '{factor_data.key}' already exists")

    async def _validate_factor_deletion(self, factor_id: UUID) -> QuotationFactor:
        """Validate factor can be deleted"""
        factor = self.factor_repo.get(factor_id)
        if not factor:
            raise NotFoundError("Quotation factor not found")
        
        await self._validate_quotation_modifiable(factor.quotation_id)
        
        # Check if factor is required for pricing calculation
        if factor.factor_type == 'product' and factor.key == 'base_rate':
            raise ConflictError("Cannot delete base rate factor")
        
        return factor

    async def _validate_factor_type_rules(self, factor_type: FactorType = None, value: Any = None) -> None:
        """Validate factor type specific business rules"""
        if not factor_type:
            return
        
        if factor_type == FactorType.DISCOUNT:
            if isinstance(value, (int, float)) and value > 1:
                raise ValidationError("Discount factor should be <= 1.0")
        
        elif factor_type == FactorType.LOADING:
            if isinstance(value, (int, float)) and value < 1:
                raise ValidationError("Loading factor should be >= 1.0")
        
        elif factor_type == FactorType.DEMOGRAPHIC:
            # Demographic factors should have impact descriptions
            pass  # Additional validation can be added here

    # ========== BUSINESS LOGIC HELPERS ==========

    async def _generate_factor_insights(self, quotation_id: UUID, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Generate business insights from factor summary"""
        insights = {
            'completeness_score': 0.0,
            'risk_level': 'medium',
            'recommendations': []
        }
        
        total_factors = summary.get('total_factors', 0)
        factors_with_descriptions = summary.get('factors_with_impact_description', 0)
        
        # Calculate completeness score
        if total_factors > 0:
            insights['completeness_score'] = factors_with_descriptions / total_factors
        
        # Generate recommendations
        if insights['completeness_score'] < 0.5:
            insights['recommendations'].append("Add impact descriptions to more factors for better transparency")
        
        if summary.get('numeric_factors', 0) == 0:
            insights['recommendations'].append("Consider adding numeric factors for automated premium calculation")
        
        # Assess risk level based on factor types
        type_counts = summary.get('factors_by_type', {})
        if type_counts.get('risk', 0) > type_counts.get('discount', 0):
            insights['risk_level'] = 'high'
        elif type_counts.get('discount', 0) > type_counts.get('loading', 0):
            insights['risk_level'] = 'low'
        
        return insights

    async def _perform_business_validations(self, quotation_id: UUID) -> Dict[str, Any]:
        """Perform business-specific factor validations"""
        factors = self.factor_repo.get_by_quotation(quotation_id)
        
        validations = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check for required factors
        required_factors = ['base_rate']
        existing_keys = [f.key for f in factors]
        
        for required_key in required_factors:
            if required_key not in existing_keys:
                validations['errors'].append(f"Missing required factor: {required_key}")
                validations['is_valid'] = False
        
        # Check for conflicting factors
        discount_factors = [f for f in factors if f.factor_type == 'discount' and f.is_numeric]
        loading_factors = [f for f in factors if f.factor_type == 'loading' and f.is_numeric]
        
        total_discount = sum(f.numeric_value or 0 for f in discount_factors)
        total_loading = sum(f.numeric_value or 0 for f in loading_factors)
        
        if total_discount > 1.0:
            validations['warnings'].append(f"Total discount factors exceed 100%: {total_discount}")
        
        if total_loading > 3.0:
            validations['warnings'].append(f"Total loading factors are very high: {total_loading}")
        
        return validations