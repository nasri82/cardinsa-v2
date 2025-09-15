# app/modules/pricing/profiles/services/pricing_profile_service.py
from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.modules.pricing.profiles.repositories.quotation_pricing_profile_repository import QuotationPricingProfileRepository
from app.modules.pricing.profiles.repositories.quotation_pricing_profile_rule_repository import QuotationPricingProfileRuleRepository
from app.modules.pricing.profiles.models.quotation_pricing_profile_model import QuotationPricingProfile

# Import the aliases that are actually used in the service code
from app.modules.pricing.profiles.schemas import (
    PricingProfileCreate,
    PricingProfileUpdate,
    PricingProfileResponse,
    PricingProfileSummary,
    PricingProfileBulkCreate,
    PricingProfileStatusUpdate,
    PricingProfileValidation,
    PricingProfileWithRules,
    InsuranceType,
    ProfileStatus,
    CurrencyCode,
)

from app.core.exceptions import (
    EntityNotFoundError,
    BusinessLogicError,
    ValidationError,
    DatabaseOperationError
)
from app.core.logging import get_logger

logger = get_logger(__name__)

# Rest of your service class code stays the same...
class PricingProfileService:
    """
    Service layer for managing pricing profiles with comprehensive business logic.
    Orchestrates repository operations and implements complex business rules.
    """
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
        self.profile_repo = QuotationPricingProfileRepository(self.db)
        self.profile_rule_repo = QuotationPricingProfileRuleRepository(self.db)
    
    # ... rest of your methods stay exactly the same
    # ============================================================================
    # PROFILE MANAGEMENT OPERATIONS
    # ============================================================================
    
    def create_pricing_profile(
        self,
        profile_data: PricingProfileCreate,
        created_by: UUID = None
    ) -> PricingProfileResponse:
        """
        Create a new pricing profile with validation and business logic.
        
        Args:
            profile_data: Profile creation data
            created_by: ID of the user creating the profile
            
        Returns:
            Created pricing profile
            
        Raises:
            ValidationError: If profile data is invalid
            BusinessLogicError: If business rules are violated
        """
        try:
            logger.info(f"Creating pricing profile: {profile_data.name}")
            
            # Validate profile data
            self._validate_profile_data(profile_data)
            
            # Check for duplicate codes
            if profile_data.code:
                existing = self.profile_repo.get_by_code(profile_data.code)
                if existing:
                    raise BusinessLogicError(f"Profile with code '{profile_data.code}' already exists")
            
            # Validate currency boundaries
            if profile_data.min_premium and profile_data.max_premium:
                if profile_data.min_premium >= profile_data.max_premium:
                    raise ValidationError("Minimum premium must be less than maximum premium")
            
            # Validate benefit exposure settings
            if profile_data.enable_benefit_exposure and not profile_data.benefit_exposure_factor:
                profile_data.benefit_exposure_factor = Decimal('1.0')
            
            # Create the profile
            profile = self.profile_repo.create_profile(
                profile_data=profile_data,
                created_by=created_by
            )
            
            logger.info(f"Successfully created pricing profile: {profile.id}")
            
            return PricingProfileResponse.from_orm(profile)
            
        except Exception as e:
            logger.error(f"Error creating pricing profile: {str(e)}")
            raise
    
    def get_pricing_profile(
        self,
        profile_id: UUID,
        include_rules: bool = False
    ) -> Optional[Union[PricingProfileResponse, PricingProfileWithRules]]:
        """
        Get a pricing profile by ID with optional rule details.
        
        Args:
            profile_id: ID of the pricing profile
            include_rules: Whether to include associated rules
            
        Returns:
            Pricing profile or None if not found
        """
        try:
            profile = self.profile_repo.get_by_id(profile_id)
            if not profile:
                return None
            
            if include_rules:
                # Get associated rules
                profile_rules = self.profile_rule_repo.get_profile_rules_ordered(profile_id)
                
                profile_dict = profile.__dict__.copy()
                profile_dict['rules'] = profile_rules
                
                return PricingProfileWithRules(**profile_dict)
            
            return PricingProfileResponse.from_orm(profile)
            
        except Exception as e:
            logger.error(f"Error getting pricing profile {profile_id}: {str(e)}")
            raise
    
    def update_pricing_profile(
        self,
        profile_id: UUID,
        profile_data: PricingProfileUpdate,
        updated_by: UUID = None
    ) -> Optional[PricingProfileResponse]:
        """
        Update an existing pricing profile.
        
        Args:
            profile_id: ID of the pricing profile
            profile_data: Updated profile data
            updated_by: ID of the user updating the profile
            
        Returns:
            Updated pricing profile or None if not found
        """
        try:
            logger.info(f"Updating pricing profile: {profile_id}")
            
            # Check if profile exists
            existing_profile = self.profile_repo.get_by_id(profile_id)
            if not existing_profile:
                raise EntityNotFoundError(f"Pricing profile {profile_id} not found")
            
            # Validate update data
            self._validate_profile_update_data(profile_data, existing_profile)
            
            # Check for duplicate codes (excluding current profile)
            if profile_data.code and profile_data.code != existing_profile.code:
                existing = self.profile_repo.get_by_code(profile_data.code)
                if existing:
                    raise BusinessLogicError(f"Profile with code '{profile_data.code}' already exists")
            
            # Create version history if significant changes
            if self._requires_versioning(profile_data, existing_profile):
                self.profile_repo.create_profile_version(
                    profile_id=profile_id,
                    version_reason="Profile update with significant changes",
                    created_by=updated_by
                )
            
            # Update the profile
            updated_profile = self.profile_repo.update_profile(
                profile_id=profile_id,
                profile_data=profile_data,
                updated_by=updated_by
            )
            
            logger.info(f"Successfully updated pricing profile: {profile_id}")
            
            return PricingProfileResponse.from_orm(updated_profile)
            
        except Exception as e:
            logger.error(f"Error updating pricing profile {profile_id}: {str(e)}")
            raise
    
    def delete_pricing_profile(
        self,
        profile_id: UUID,
        updated_by: UUID = None,
        hard_delete: bool = False
    ) -> bool:
        """
        Delete a pricing profile (soft delete by default).
        
        Args:
            profile_id: ID of the pricing profile
            updated_by: ID of the user deleting the profile
            hard_delete: Whether to permanently delete
            
        Returns:
            True if successfully deleted
        """
        try:
            logger.info(f"Deleting pricing profile: {profile_id}")
            
            # Check if profile exists
            profile = self.profile_repo.get_by_id(profile_id)
            if not profile:
                raise EntityNotFoundError(f"Pricing profile {profile_id} not found")
            
            # Check if profile is in use
            usage_check = self.check_profile_usage(profile_id)
            if usage_check['is_in_use'] and not hard_delete:
                raise BusinessLogicError(
                    f"Cannot delete profile '{profile.name}' - it is currently in use. "
                    f"Used in {usage_check['quotation_count']} quotations."
                )
            
            # Delete the profile
            success = self.profile_repo.delete_profile(
                profile_id=profile_id,
                updated_by=updated_by,
                hard_delete=hard_delete
            )
            
            if success:
                logger.info(f"Successfully deleted pricing profile: {profile_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting pricing profile {profile_id}: {str(e)}")
            raise
    
    # ============================================================================
    # PROFILE SEARCH AND FILTERING
    # ============================================================================
    
    def search_pricing_profiles(
        self,
        name: str = None,
        code: str = None,
        insurance_type: str = None,
        is_active: bool = None,
        currency: str = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search pricing profiles with various filters.
        
        Args:
            name: Filter by profile name (partial match)
            code: Filter by profile code
            insurance_type: Filter by insurance type
            is_active: Filter by active status
            currency: Filter by currency
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            Dictionary with search results and pagination
        """
        try:
            results = self.profile_repo.search_profiles(
                name=name,
                code=code,
                insurance_type=insurance_type,
                is_active=is_active,
                currency=currency,
                limit=limit,
                offset=offset
            )
            
            # Convert to response models
            profiles = [PricingProfileResponse.from_orm(profile) for profile in results['profiles']]
            
            return {
                'profiles': profiles,
                'pagination': results['pagination'],
                'filters_applied': results['filters_applied']
            }
            
        except Exception as e:
            logger.error(f"Error searching pricing profiles: {str(e)}")
            raise
    
    def get_profiles_by_insurance_type(
        self,
        insurance_type: str,
        active_only: bool = True
    ) -> List[PricingProfileResponse]:
        """
        Get all profiles for a specific insurance type.
        
        Args:
            insurance_type: Type of insurance (Medical, Motor, Life, etc.)
            active_only: Whether to return only active profiles
            
        Returns:
            List of pricing profiles
        """
        try:
            profiles = self.profile_repo.get_by_insurance_type(
                insurance_type=insurance_type,
                active_only=active_only
            )
            
            return [PricingProfileResponse.from_orm(profile) for profile in profiles]
            
        except Exception as e:
            logger.error(f"Error getting profiles for insurance type {insurance_type}: {str(e)}")
            raise
    
    # ============================================================================
    # PROFILE RULE MANAGEMENT
    # ============================================================================
    
    def add_rule_to_profile(
        self,
        profile_id: UUID,
        rule_id: UUID,
        order_index: int = None,
        created_by: UUID = None
    ) -> Dict[str, Any]:
        """
        Add a pricing rule to a profile.
        
        Args:
            profile_id: ID of the pricing profile
            rule_id: ID of the pricing rule
            order_index: Execution order (auto-assigned if None)
            created_by: ID of the user adding the rule
            
        Returns:
            Dictionary with operation result
        """
        try:
            logger.info(f"Adding rule {rule_id} to profile {profile_id}")
            
            # Validate profile exists
            profile = self.profile_repo.get_by_id(profile_id)
            if not profile:
                raise EntityNotFoundError(f"Pricing profile {profile_id} not found")
            
            # Auto-assign order index if not provided
            if order_index is None:
                existing_rules = self.profile_rule_repo.get_by_profile_id(profile_id)
                order_index = len(existing_rules)
            
            # Add the rule
            profile_rule = self.profile_rule_repo.create_profile_rule(
                profile_id=profile_id,
                rule_id=rule_id,
                order_index=order_index,
                created_by=created_by
            )
            
            logger.info(f"Successfully added rule {rule_id} to profile {profile_id}")
            
            return {
                'success': True,
                'profile_rule_id': profile_rule.id,
                'order_index': profile_rule.order_index,
                'message': f'Rule successfully added to profile'
            }
            
        except Exception as e:
            logger.error(f"Error adding rule to profile: {str(e)}")
            raise
    
    def remove_rule_from_profile(
        self,
        profile_id: UUID,
        rule_id: UUID,
        updated_by: UUID = None
    ) -> Dict[str, Any]:
        """
        Remove a pricing rule from a profile.
        
        Args:
            profile_id: ID of the pricing profile
            rule_id: ID of the pricing rule
            updated_by: ID of the user removing the rule
            
        Returns:
            Dictionary with operation result
        """
        try:
            logger.info(f"Removing rule {rule_id} from profile {profile_id}")
            
            success = self.profile_rule_repo.remove_rule_from_profile(
                profile_id=profile_id,
                rule_id=rule_id,
                updated_by=updated_by
            )
            
            if success:
                logger.info(f"Successfully removed rule {rule_id} from profile {profile_id}")
                return {
                    'success': True,
                    'message': 'Rule successfully removed from profile'
                }
            else:
                return {
                    'success': False,
                    'message': 'Rule-profile relationship not found'
                }
            
        except Exception as e:
            logger.error(f"Error removing rule from profile: {str(e)}")
            raise
    
    def reorder_profile_rules(
        self,
        profile_id: UUID,
        rule_orders: Dict[UUID, int],
        updated_by: UUID = None
    ) -> Dict[str, Any]:
        """
        Reorder rules within a profile.
        
        Args:
            profile_id: ID of the pricing profile
            rule_orders: Dictionary mapping rule_id to new order_index
            updated_by: ID of the user reordering rules
            
        Returns:
            Dictionary with operation result
        """
        try:
            logger.info(f"Reordering rules for profile {profile_id}")
            
            updated_rules = self.profile_rule_repo.reorder_profile_rules(
                profile_id=profile_id,
                rule_orders=rule_orders,
                updated_by=updated_by
            )
            
            logger.info(f"Successfully reordered {len(updated_rules)} rules for profile {profile_id}")
            
            return {
                'success': True,
                'updated_rules_count': len(updated_rules),
                'message': f'Successfully reordered {len(updated_rules)} rules'
            }
            
        except Exception as e:
            logger.error(f"Error reordering profile rules: {str(e)}")
            raise
    
    # ============================================================================
    # PROFILE ANALYSIS AND VALIDATION
    # ============================================================================
    
    def validate_profile_configuration(self, profile_id: UUID) -> Dict[str, Any]:
        """
        Validate the complete configuration of a pricing profile.
        
        Args:
            profile_id: ID of the pricing profile
            
        Returns:
            Dictionary with validation results
        """
        try:
            # Get profile details
            profile = self.profile_repo.get_by_id(profile_id)
            if not profile:
                raise EntityNotFoundError(f"Pricing profile {profile_id} not found")
            
            issues = []
            warnings = []
            
            # Validate profile basic configuration
            if not profile.name or len(profile.name.strip()) == 0:
                issues.append("Profile name is required")
            
            if not profile.insurance_type:
                warnings.append("Insurance type not specified")
            
            if not profile.currency or len(profile.currency) != 3:
                issues.append("Valid 3-letter currency code is required")
            
            # Validate premium boundaries
            if profile.min_premium and profile.max_premium:
                if profile.min_premium >= profile.max_premium:
                    issues.append("Minimum premium must be less than maximum premium")
            
            # Validate benefit exposure configuration
            if profile.enable_benefit_exposure:
                if not profile.benefit_exposure_factor:
                    warnings.append("Benefit exposure factor not set despite being enabled")
                elif profile.benefit_exposure_factor <= 0:
                    issues.append("Benefit exposure factor must be positive")
            
            # Validate network cost integration
            if profile.enable_network_costs and not profile.network_cost_factor:
                warnings.append("Network cost factor not set despite being enabled")
            
            # Validate rule consistency
            rule_validation = self.profile_rule_repo.validate_profile_rule_consistency(profile_id)
            if rule_validation['issues']:
                issues.extend(rule_validation['issues'])
            if rule_validation['warnings']:
                warnings.extend(rule_validation['warnings'])
            
            # Check for risk formula if specified
            if profile.risk_formula:
                try:
                    # Basic syntax validation for risk formula
                    self._validate_risk_formula(profile.risk_formula)
                except Exception as e:
                    issues.append(f"Invalid risk formula: {str(e)}")
            
            return {
                'profile_id': profile_id,
                'profile_name': profile.name,
                'is_valid': len(issues) == 0,
                'issues': issues,
                'warnings': warnings,
                'rules_validation': rule_validation,
                'validation_timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error validating profile configuration: {str(e)}")
            raise
    
    def check_profile_usage(self, profile_id: UUID) -> Dict[str, Any]:
        """
        Check how a profile is being used in the system.
        
        Args:
            profile_id: ID of the pricing profile
            
        Returns:
            Dictionary with usage information
        """
        try:
            # Note: This would need to be implemented when quotation module is available
            # For now, return basic structure
            
            usage_info = {
                'profile_id': profile_id,
                'is_in_use': False,
                'quotation_count': 0,
                'active_quotations': 0,
                'recent_usage': [],
                'last_used': None
            }
            
            # TODO: Implement actual usage checking when quotation tables are available
            # This would query quotation tables to find usage
            
            return usage_info
            
        except Exception as e:
            logger.error(f"Error checking profile usage: {str(e)}")
            raise
    
    def get_profile_analytics(self, profile_id: UUID) -> Dict[str, Any]:
        """
        Get comprehensive analytics for a pricing profile.
        
        Args:
            profile_id: ID of the pricing profile
            
        Returns:
            Dictionary with profile analytics
        """
        try:
            profile = self.profile_repo.get_by_id(profile_id)
            if not profile:
                raise EntityNotFoundError(f"Pricing profile {profile_id} not found")
            
            # Get rule summary
            rule_summary = self.profile_rule_repo.get_profile_rule_summary(profile_id)
            
            # Get usage information
            usage_info = self.check_profile_usage(profile_id)
            
            # Get validation status
            validation_result = self.validate_profile_configuration(profile_id)
            
            return {
                'profile_id': profile_id,
                'profile_name': profile.name,
                'profile_code': profile.code,
                'insurance_type': profile.insurance_type,
                'is_active': profile.is_active,
                'created_at': profile.created_at,
                'last_updated': profile.updated_at,
                'rule_analytics': rule_summary,
                'usage_analytics': usage_info,
                'validation_status': {
                    'is_valid': validation_result['is_valid'],
                    'issues_count': len(validation_result['issues']),
                    'warnings_count': len(validation_result['warnings'])
                },
                'configuration_summary': {
                    'has_risk_formula': bool(profile.risk_formula),
                    'benefit_exposure_enabled': profile.enable_benefit_exposure,
                    'network_costs_enabled': profile.enable_network_costs,
                    'has_premium_boundaries': bool(profile.min_premium and profile.max_premium),
                    'currency': profile.currency
                },
                'analytics_timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error getting profile analytics: {str(e)}")
            raise
    
    # ============================================================================
    # PROFILE OPERATIONS
    # ============================================================================
    
    def clone_pricing_profile(
        self,
        source_profile_id: UUID,
        new_name: str,
        new_code: str = None,
        include_rules: bool = True,
        created_by: UUID = None
    ) -> PricingProfileResponse:
        """
        Clone an existing pricing profile with optional rule copying.
        
        Args:
            source_profile_id: ID of the profile to clone
            new_name: Name for the new profile
            new_code: Code for the new profile (optional)
            include_rules: Whether to copy associated rules
            created_by: ID of the user creating the clone
            
        Returns:
            Newly created profile
        """
        try:
            logger.info(f"Cloning pricing profile {source_profile_id} as '{new_name}'")
            
            # Get source profile
            source_profile = self.profile_repo.get_by_id(source_profile_id)
            if not source_profile:
                raise EntityNotFoundError(f"Source profile {source_profile_id} not found")
            
            # Create clone data
            clone_data = PricingProfileCreate(
                name=new_name,
                description=f"Cloned from: {source_profile.name}",
                code=new_code,
                insurance_type=source_profile.insurance_type,
                currency=source_profile.currency,
                min_premium=source_profile.min_premium,
                max_premium=source_profile.max_premium,
                risk_formula=source_profile.risk_formula,
                enable_benefit_exposure=source_profile.enable_benefit_exposure,
                benefit_exposure_factor=source_profile.benefit_exposure_factor,
                enable_network_costs=source_profile.enable_network_costs,
                network_cost_factor=source_profile.network_cost_factor,
                is_active=False  # New profiles start as inactive
            )
            
            # Create the cloned profile
            cloned_profile = self.create_pricing_profile(
                profile_data=clone_data,
                created_by=created_by
            )
            
            # Copy rules if requested
            if include_rules:
                copied_rules = self.profile_rule_repo.copy_rules_between_profiles(
                    source_profile_id=source_profile_id,
                    target_profile_id=cloned_profile.id,
                    created_by=created_by,
                    preserve_order=True
                )
                
                logger.info(f"Copied {len(copied_rules)} rules to cloned profile")
            
            logger.info(f"Successfully cloned profile {source_profile_id} as {cloned_profile.id}")
            
            return cloned_profile
            
        except Exception as e:
            logger.error(f"Error cloning pricing profile: {str(e)}")
            raise
    
    def activate_profile(
        self,
        profile_id: UUID,
        updated_by: UUID = None
    ) -> PricingProfileResponse:
        """
        Activate a pricing profile after validation.
        
        Args:
            profile_id: ID of the pricing profile
            updated_by: ID of the user activating the profile
            
        Returns:
            Updated profile
        """
        try:
            logger.info(f"Activating pricing profile: {profile_id}")
            
            # Validate profile configuration before activation
            validation_result = self.validate_profile_configuration(profile_id)
            if not validation_result['is_valid']:
                raise BusinessLogicError(
                    f"Cannot activate profile with validation issues: {validation_result['issues']}"
                )
            
            # Update profile status
            profile_data = PricingProfileUpdate(is_active=True)
            updated_profile = self.update_pricing_profile(
                profile_id=profile_id,
                profile_data=profile_data,
                updated_by=updated_by
            )
            
            logger.info(f"Successfully activated pricing profile: {profile_id}")
            
            return updated_profile
            
        except Exception as e:
            logger.error(f"Error activating pricing profile: {str(e)}")
            raise
    
    def deactivate_profile(
        self,
        profile_id: UUID,
        updated_by: UUID = None
    ) -> PricingProfileResponse:
        """
        Deactivate a pricing profile.
        
        Args:
            profile_id: ID of the pricing profile
            updated_by: ID of the user deactivating the profile
            
        Returns:
            Updated profile
        """
        try:
            logger.info(f"Deactivating pricing profile: {profile_id}")
            
            # Check if profile is currently in use
            usage_info = self.check_profile_usage(profile_id)
            if usage_info['active_quotations'] > 0:
                raise BusinessLogicError(
                    f"Cannot deactivate profile with {usage_info['active_quotations']} active quotations"
                )
            
            # Update profile status
            profile_data = PricingProfileUpdate(is_active=False)
            updated_profile = self.update_pricing_profile(
                profile_id=profile_id,
                profile_data=profile_data,
                updated_by=updated_by
            )
            
            logger.info(f"Successfully deactivated pricing profile: {profile_id}")
            
            return updated_profile
            
        except Exception as e:
            logger.error(f"Error deactivating pricing profile: {str(e)}")
            raise
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def _validate_profile_data(self, profile_data: PricingProfileCreate) -> None:
        """Validate profile creation data."""
        if not profile_data.name or len(profile_data.name.strip()) == 0:
            raise ValidationError("Profile name is required")
        
        if len(profile_data.name) > 255:
            raise ValidationError("Profile name cannot exceed 255 characters")
        
        if profile_data.code and len(profile_data.code) > 50:
            raise ValidationError("Profile code cannot exceed 50 characters")
        
        if profile_data.currency and len(profile_data.currency) != 3:
            raise ValidationError("Currency must be a valid 3-letter code")
        
        if profile_data.min_premium and profile_data.min_premium < 0:
            raise ValidationError("Minimum premium cannot be negative")
        
        if profile_data.max_premium and profile_data.max_premium < 0:
            raise ValidationError("Maximum premium cannot be negative")
    
    def _validate_profile_update_data(
        self, 
        profile_data: PricingProfileUpdate, 
        existing_profile: QuotationPricingProfile
    ) -> None:
        """Validate profile update data."""
        if profile_data.name is not None:
            if not profile_data.name or len(profile_data.name.strip()) == 0:
                raise ValidationError("Profile name cannot be empty")
            if len(profile_data.name) > 255:
                raise ValidationError("Profile name cannot exceed 255 characters")
        
        if profile_data.code is not None and len(profile_data.code) > 50:
            raise ValidationError("Profile code cannot exceed 50 characters")
        
        if profile_data.currency is not None and len(profile_data.currency) != 3:
            raise ValidationError("Currency must be a valid 3-letter code")
        
        if profile_data.min_premium is not None and profile_data.min_premium < 0:
            raise ValidationError("Minimum premium cannot be negative")
        
        if profile_data.max_premium is not None and profile_data.max_premium < 0:
            raise ValidationError("Maximum premium cannot be negative")
    
    def _requires_versioning(
        self, 
        profile_data: PricingProfileUpdate, 
        existing_profile: QuotationPricingProfile
    ) -> bool:
        """Check if changes require version history."""
        significant_fields = [
            'risk_formula', 'min_premium', 'max_premium', 
            'benefit_exposure_factor', 'network_cost_factor'
        ]
        
        for field in significant_fields:
            if hasattr(profile_data, field) and getattr(profile_data, field) is not None:
                if getattr(profile_data, field) != getattr(existing_profile, field):
                    return True
        
        return False
    
    def _validate_risk_formula(self, formula: str) -> None:
        """Basic validation of risk formula syntax."""
        if not formula or len(formula.strip()) == 0:
            raise ValidationError("Risk formula cannot be empty")
        
        # Basic syntax checks - extend as needed
        forbidden_keywords = ['import', 'exec', 'eval', '__']
        for keyword in forbidden_keywords:
            if keyword in formula.lower():
                raise ValidationError(f"Risk formula contains forbidden keyword: {keyword}")
        
        # Additional validation logic can be added here
        # Such as checking for valid variables, operators, functions, etc.