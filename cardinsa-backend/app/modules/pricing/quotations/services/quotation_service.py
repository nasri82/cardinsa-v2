# app/modules/insurance/quotations/services/quotation_service.py

from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging

from ..models import Quotation, QuotationStatusEnum
from ..schemas import (
    QuotationCreate, QuotationUpdate, QuotationResponse, QuotationSummary,
    QuotationStatus, QuotationStatusUpdate, QuotationCalculationRequest
)
from ..repositories import QuotationRepository, QuotationItemRepository, QuotationFactorRepository
from .quotation_item_service import QuotationItemService
from .quotation_factor_service import QuotationFactorService
from .quotation_workflow_service import QuotationWorkflowService
from app.core.exceptions import (
    BusinessLogicError, ValidationError, NotFoundError, 
    ConflictError, UnauthorizedError
)


logger = logging.getLogger(__name__)


class QuotationService:
    """
    Service class for Quotation business logic
    
    Orchestrates quotation operations including creation, status management,
    premium calculations, workflow automation, and business rule enforcement.
    """

    def __init__(self, db: Session):
        self.db = db
        self.quotation_repo = QuotationRepository(db)
        self.item_repo = QuotationItemRepository(db)
        self.factor_repo = QuotationFactorRepository(db)
        self.item_service = QuotationItemService(db)
        self.factor_service = QuotationFactorService(db)
        self.workflow_service = QuotationWorkflowService(db)

    # ========== CREATE OPERATIONS ==========

    async def create_quotation(self, quotation_data: QuotationCreate, 
                              created_by: UUID = None) -> QuotationResponse:
        """Create a new quotation with business validations"""
        try:
            # Validate business rules
            await self._validate_quotation_creation(quotation_data)
            
            # Create quotation
            quotation = self.quotation_repo.create_quotation(quotation_data, created_by)
            
            # Log creation event
            await self.workflow_service.log_event(
                quotation_id=quotation.id,
                event="quotation_created",
                notes=f"Quotation created for customer: {quotation.customer_name}",
                created_by=created_by
            )
            
            # Initialize default factors if product code is provided
            if quotation.product_code:
                await self._initialize_default_factors(quotation.id, quotation.product_code, created_by)
            
            logger.info(f"Created quotation {quotation.id} for customer {quotation.customer_name}")
            
            return QuotationResponse.from_orm(quotation)
            
        except Exception as e:
            logger.error(f"Error creating quotation: {str(e)}")
            raise BusinessLogicError(f"Failed to create quotation: {str(e)}")

    async def create_quotation_with_items(self, quotation_data: QuotationCreate,
                                        items_data: List[Dict], 
                                        created_by: UUID = None) -> QuotationResponse:
        """Create quotation with coverage items in single transaction"""
        try:
            # Validate quotation and items
            await self._validate_quotation_creation(quotation_data)
            await self._validate_items_data(items_data)
            
            # Create quotation with items
            quotation = self.quotation_repo.create_with_items_and_factors(
                quotation_data=quotation_data,
                items_data=items_data,
                created_by=created_by
            )
            
            # Log creation with items
            await self.workflow_service.log_event(
                quotation_id=quotation.id,
                event="quotation_created",
                notes=f"Quotation created with {len(items_data)} coverage items",
                created_by=created_by
            )
            
            logger.info(f"Created quotation {quotation.id} with {len(items_data)} items")
            
            return QuotationResponse.from_orm(quotation)
            
        except Exception as e:
            logger.error(f"Error creating quotation with items: {str(e)}")
            raise BusinessLogicError(f"Failed to create quotation with items: {str(e)}")

    # ========== READ OPERATIONS ==========

    async def get_quotation(self, quotation_id: UUID, 
                           load_relations: bool = False) -> Optional[QuotationResponse]:
        """Get quotation by ID with optional relationship loading"""
        try:
            if load_relations:
                quotation = self.quotation_repo.get_with_all_relations(quotation_id)
            else:
                quotation = self.quotation_repo.get(quotation_id)
            
            if not quotation:
                return None
            
            return QuotationResponse.from_orm(quotation)
            
        except Exception as e:
            logger.error(f"Error retrieving quotation {quotation_id}: {str(e)}")
            raise BusinessLogicError(f"Failed to retrieve quotation: {str(e)}")

    async def get_quotation_by_quote_number(self, quote_number: str) -> Optional[QuotationResponse]:
        """Get quotation by quote number"""
        try:
            quotation = self.quotation_repo.get_by_quote_number(quote_number)
            if not quotation:
                return None
            
            return QuotationResponse.from_orm(quotation)
            
        except Exception as e:
            logger.error(f"Error retrieving quotation by quote number {quote_number}: {str(e)}")
            raise BusinessLogicError(f"Failed to retrieve quotation: {str(e)}")

    async def get_customer_quotations(self, customer_id: UUID = None, 
                                    customer_email: str = None,
                                    limit: int = 50) -> List[QuotationSummary]:
        """Get quotations for a customer"""
        try:
            if customer_id:
                quotations = self.quotation_repo.get_by_customer(customer_id, limit)
            elif customer_email:
                quotations = self.quotation_repo.get_by_customer_email(customer_email, limit)
            else:
                raise ValidationError("Either customer_id or customer_email must be provided")
            
            return [QuotationSummary.from_orm(q) for q in quotations]
            
        except Exception as e:
            logger.error(f"Error retrieving customer quotations: {str(e)}")
            raise BusinessLogicError(f"Failed to retrieve customer quotations: {str(e)}")

    async def search_quotations(self, search_term: str, 
                               limit: int = 50) -> List[QuotationSummary]:
        """Search quotations across multiple fields"""
        try:
            quotations = self.quotation_repo.search_quotations(search_term, limit)
            return [QuotationSummary.from_orm(q) for q in quotations]
            
        except Exception as e:
            logger.error(f"Error searching quotations: {str(e)}")
            raise BusinessLogicError(f"Failed to search quotations: {str(e)}")

    async def get_quotations_paginated(self, page: int = 1, per_page: int = 50,
                                     filters: Dict[str, Any] = None) -> Tuple[List[QuotationSummary], int]:
        """Get paginated quotations with filters"""
        try:
            quotations, total = self.quotation_repo.get_quotations_paginated(page, per_page, filters)
            
            summaries = [QuotationSummary.from_orm(q) for q in quotations]
            return summaries, total
            
        except Exception as e:
            logger.error(f"Error retrieving paginated quotations: {str(e)}")
            raise BusinessLogicError(f"Failed to retrieve quotations: {str(e)}")

    # ========== UPDATE OPERATIONS ==========

    async def update_quotation(self, quotation_id: UUID, quotation_data: QuotationUpdate,
                              updated_by: UUID = None) -> Optional[QuotationResponse]:
        """Update quotation with business validations"""
        try:
            # Check if quotation exists and is not locked
            quotation = await self._validate_quotation_update(quotation_id)
            
            # Validate update data
            await self._validate_quotation_update_data(quotation_data)
            
            # Update quotation
            updated_quotation = self.quotation_repo.update(quotation_id, quotation_data, updated_by)
            
            # Log update event
            await self.workflow_service.log_event(
                quotation_id=quotation_id,
                event="quotation_modified",
                notes="Quotation details updated",
                created_by=updated_by
            )
            
            logger.info(f"Updated quotation {quotation_id}")
            
            return QuotationResponse.from_orm(updated_quotation) if updated_quotation else None
            
        except Exception as e:
            logger.error(f"Error updating quotation {quotation_id}: {str(e)}")
            raise BusinessLogicError(f"Failed to update quotation: {str(e)}")

    async def update_status(self, quotation_id: UUID, status_update: QuotationStatusUpdate,
                           updated_by: UUID = None) -> Optional[QuotationResponse]:
        """Update quotation status with workflow validation"""
        try:
            # Validate status transition
            quotation = await self._validate_status_transition(quotation_id, status_update.status)
            
            # Update status
            updated_quotation = self.quotation_repo.update_status(
                quotation_id=quotation_id,
                new_status=status_update.status,
                updated_by=updated_by,
                notes=status_update.notes
            )
            
            # Trigger workflow actions based on new status
            await self._handle_status_change(quotation_id, status_update.status, updated_by)
            
            logger.info(f"Updated quotation {quotation_id} status to {status_update.status}")
            
            return QuotationResponse.from_orm(updated_quotation) if updated_quotation else None
            
        except Exception as e:
            logger.error(f"Error updating quotation status: {str(e)}")
            raise BusinessLogicError(f"Failed to update quotation status: {str(e)}")

    async def calculate_premium(self, quotation_id: UUID, 
                               calculation_request: QuotationCalculationRequest,
                               calculated_by: UUID = None) -> Optional[QuotationResponse]:
        """Calculate quotation premium with all factors"""
        try:
            quotation = await self._validate_quotation_calculation(quotation_id)
            
            # Get all factors for calculation
            factors = self.factor_repo.get_by_quotation(quotation_id)
            
            # Apply override factors if provided
            if calculation_request.override_factors:
                await self._apply_override_factors(quotation_id, calculation_request.override_factors)
                factors = self.factor_repo.get_by_quotation(quotation_id)  # Refresh factors
            
            # Perform premium calculation
            premium_data = await self._calculate_premium_components(quotation, factors)
            
            # Update quotation with calculated premiums
            updated_quotation = self.quotation_repo.update_premium(
                quotation_id=quotation_id,
                premium_data=premium_data,
                updated_by=calculated_by
            )
            
            # Update status to calculated if currently draft
            if quotation.status == QuotationStatusEnum.DRAFT:
                await self.update_status(
                    quotation_id=quotation_id,
                    status_update=QuotationStatusUpdate(
                        status=QuotationStatus.CALCULATED,
                        notes="Premium calculated automatically"
                    ),
                    updated_by=calculated_by
                )
            
            # Log calculation event
            await self.workflow_service.log_event(
                quotation_id=quotation_id,
                event="premium_calculated",
                notes=f"Premium calculated: {premium_data.get('total_premium', 0)}",
                created_by=calculated_by
            )
            
            logger.info(f"Calculated premium for quotation {quotation_id}: {premium_data.get('total_premium', 0)}")
            
            return QuotationResponse.from_orm(updated_quotation) if updated_quotation else None
            
        except Exception as e:
            logger.error(f"Error calculating premium for quotation {quotation_id}: {str(e)}")
            raise BusinessLogicError(f"Failed to calculate premium: {str(e)}")

    async def lock_quotation(self, quotation_id: UUID, lock_reason: str,
                            locked_by: UUID) -> Optional[QuotationResponse]:
        """Lock quotation to prevent modifications"""
        try:
            quotation = self.quotation_repo.get(quotation_id)
            if not quotation:
                raise NotFoundError("Quotation not found")
            
            if quotation.is_locked:
                raise ConflictError("Quotation is already locked")
            
            # Lock quotation
            locked_quotation = self.quotation_repo.lock_quotation(quotation_id, lock_reason, locked_by)
            
            # Log lock event
            await self.workflow_service.log_event(
                quotation_id=quotation_id,
                event="quotation_locked",
                notes=f"Locked: {lock_reason}",
                created_by=locked_by
            )
            
            logger.info(f"Locked quotation {quotation_id}: {lock_reason}")
            
            return QuotationResponse.from_orm(locked_quotation) if locked_quotation else None
            
        except Exception as e:
            logger.error(f"Error locking quotation {quotation_id}: {str(e)}")
            raise BusinessLogicError(f"Failed to lock quotation: {str(e)}")

    async def unlock_quotation(self, quotation_id: UUID, 
                              unlocked_by: UUID) -> Optional[QuotationResponse]:
        """Unlock quotation to allow modifications"""
        try:
            quotation = self.quotation_repo.get(quotation_id)
            if not quotation:
                raise NotFoundError("Quotation not found")
            
            if not quotation.is_locked:
                raise ConflictError("Quotation is not locked")
            
            # Unlock quotation
            unlocked_quotation = self.quotation_repo.unlock_quotation(quotation_id, unlocked_by)
            
            # Log unlock event
            await self.workflow_service.log_event(
                quotation_id=quotation_id,
                event="quotation_unlocked",
                notes="Quotation unlocked",
                created_by=unlocked_by
            )
            
            logger.info(f"Unlocked quotation {quotation_id}")
            
            return QuotationResponse.from_orm(unlocked_quotation) if unlocked_quotation else None
            
        except Exception as e:
            logger.error(f"Error unlocking quotation {quotation_id}: {str(e)}")
            raise BusinessLogicError(f"Failed to unlock quotation: {str(e)}")

    # ========== DELETE OPERATIONS ==========

    async def delete_quotation(self, quotation_id: UUID, 
                              deleted_by: UUID = None) -> bool:
        """Soft delete quotation"""
        try:
            quotation = await self._validate_quotation_deletion(quotation_id)
            
            # Soft delete quotation
            success = self.quotation_repo.soft_delete(quotation_id, deleted_by)
            
            if success:
                # Log deletion event
                await self.workflow_service.log_event(
                    quotation_id=quotation_id,
                    event="quotation_deleted",
                    notes="Quotation soft deleted",
                    created_by=deleted_by
                )
                
                logger.info(f"Deleted quotation {quotation_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting quotation {quotation_id}: {str(e)}")
            raise BusinessLogicError(f"Failed to delete quotation: {str(e)}")

    # ========== ANALYTICS & REPORTING ==========

    async def get_quotation_statistics(self, date_from: date = None, 
                                     date_to: date = None) -> Dict[str, Any]:
        """Get comprehensive quotation statistics"""
        try:
            stats = self.quotation_repo.get_statistics(date_from, date_to)
            
            # Add additional metrics
            conversion_rate = self.quotation_repo.get_conversion_rate(date_from, date_to)
            stats['conversion_rate'] = conversion_rate
            
            # Add period information
            stats['period'] = {
                'from': date_from.isoformat() if date_from else None,
                'to': date_to.isoformat() if date_to else None,
                'days': (date_to - date_from).days if date_from and date_to else None
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error retrieving quotation statistics: {str(e)}")
            raise BusinessLogicError(f"Failed to retrieve statistics: {str(e)}")

    # ========== BUSINESS VALIDATION METHODS ==========

    async def _validate_quotation_creation(self, quotation_data: QuotationCreate) -> None:
        """Validate quotation creation business rules"""
        # Check for duplicate quote number if provided
        if quotation_data.quote_number:
            if self.quotation_repo.exists_by_quote_number(quotation_data.quote_number):
                raise ConflictError(f"Quote number {quotation_data.quote_number} already exists")
        
        # Validate customer data
        if not quotation_data.customer_name or len(quotation_data.customer_name.strip()) == 0:
            raise ValidationError("Customer name is required")
        
        # Validate email format if provided
        if quotation_data.customer_email:
            # Email validation is handled by Pydantic schema
            pass
        
        # Validate currency code
        if quotation_data.currency_code:
            # Currency validation is handled by Pydantic schema
            pass

    async def _validate_quotation_update(self, quotation_id: UUID) -> Quotation:
        """Validate quotation can be updated"""
        quotation = self.quotation_repo.get(quotation_id)
        if not quotation:
            raise NotFoundError("Quotation not found")
        
        if quotation.is_locked:
            raise ConflictError("Cannot update locked quotation")
        
        if quotation.status in [QuotationStatusEnum.CONVERTED, QuotationStatusEnum.EXPIRED]:
            raise ConflictError(f"Cannot update quotation in {quotation.status} status")
        
        return quotation

    async def _validate_status_transition(self, quotation_id: UUID, new_status: QuotationStatus) -> Quotation:
        """Validate status transition is allowed"""
        quotation = self.quotation_repo.get(quotation_id)
        if not quotation:
            raise NotFoundError("Quotation not found")
        
        # Define allowed transitions
        allowed_transitions = {
            QuotationStatusEnum.DRAFT: [QuotationStatusEnum.IN_PROGRESS, QuotationStatusEnum.CALCULATED],
            QuotationStatusEnum.IN_PROGRESS: [QuotationStatusEnum.CALCULATED, QuotationStatusEnum.DRAFT],
            QuotationStatusEnum.CALCULATED: [QuotationStatusEnum.PENDING_APPROVAL, QuotationStatusEnum.APPROVED, QuotationStatusEnum.IN_PROGRESS],
            QuotationStatusEnum.PENDING_APPROVAL: [QuotationStatusEnum.APPROVED, QuotationStatusEnum.REJECTED, QuotationStatusEnum.CALCULATED],
            QuotationStatusEnum.APPROVED: [QuotationStatusEnum.CONVERTED, QuotationStatusEnum.EXPIRED],
            QuotationStatusEnum.REJECTED: [QuotationStatusEnum.DRAFT, QuotationStatusEnum.CALCULATED],
            QuotationStatusEnum.CONVERTED: [],  # Terminal status
            QuotationStatusEnum.EXPIRED: [QuotationStatusEnum.DRAFT],  # Can restart
            QuotationStatusEnum.CANCELLED: []   # Terminal status
        }
        
        current_status = QuotationStatusEnum(quotation.status)
        target_status = QuotationStatusEnum(new_status.value)
        
        if target_status not in allowed_transitions.get(current_status, []):
            raise ConflictError(f"Cannot transition from {current_status.value} to {target_status.value}")
        
        return quotation

    async def _validate_quotation_calculation(self, quotation_id: UUID) -> Quotation:
        """Validate quotation can be calculated"""
        quotation = self.quotation_repo.get(quotation_id)
        if not quotation:
            raise NotFoundError("Quotation not found")
        
        if quotation.is_locked:
            raise ConflictError("Cannot calculate premium for locked quotation")
        
        # Check if quotation has items
        items_count = self.item_repo.get_items_count_by_quotation(quotation_id)
        if items_count == 0:
            raise ValidationError("Cannot calculate premium without coverage items")
        
        return quotation

    async def _validate_quotation_deletion(self, quotation_id: UUID) -> Quotation:
        """Validate quotation can be deleted"""
        quotation = self.quotation_repo.get(quotation_id)
        if not quotation:
            raise NotFoundError("Quotation not found")
        
        if quotation.status == QuotationStatusEnum.CONVERTED:
            raise ConflictError("Cannot delete converted quotation")
        
        if quotation.is_locked:
            raise ConflictError("Cannot delete locked quotation")
        
        return quotation

    # ========== BUSINESS LOGIC HELPERS ==========

    async def _initialize_default_factors(self, quotation_id: UUID, product_code: str, 
                                         created_by: UUID = None) -> None:
        """Initialize default factors based on product code"""
        # This would typically load default factors from product configuration
        default_factors = await self._get_default_factors_for_product(product_code)
        
        for factor_key, factor_data in default_factors.items():
            await self.factor_service.create_factor(
                quotation_id=quotation_id,
                key=factor_key,
                value=factor_data['value'],
                factor_type=factor_data.get('type'),
                impact_description=factor_data.get('description'),
                created_by=created_by
            )

    async def _get_default_factors_for_product(self, product_code: str) -> Dict[str, Dict]:
        """Get default factors configuration for product"""
        # This would typically come from a product configuration service
        default_configs = {
            'MOTOR_COMP': {
                'base_rate': {'value': 1.0, 'type': 'product', 'description': 'Base comprehensive rate'},
                'vehicle_age_factor': {'value': 1.0, 'type': 'risk', 'description': 'Vehicle age adjustment'},
                'driver_age_factor': {'value': 1.0, 'type': 'demographic', 'description': 'Driver age adjustment'}
            },
            'MOTOR_TPL': {
                'base_rate': {'value': 1.0, 'type': 'product', 'description': 'Base third party rate'},
                'driver_age_factor': {'value': 1.0, 'type': 'demographic', 'description': 'Driver age adjustment'}
            }
        }
        
        return default_configs.get(product_code, {})

    async def _calculate_premium_components(self, quotation: Quotation, 
                                          factors: List) -> Dict[str, Decimal]:
        """Calculate all premium components"""
        # Get base premium (could come from pricing tables)
        base_premium = quotation.base_premium or Decimal('1000.00')
        
        # Apply all factors
        total_factor = Decimal('1.0')
        discount_amount = Decimal('0.0')
        surcharge_amount = Decimal('0.0')
        
        for factor in factors:
            if factor.is_numeric and factor.numeric_value:
                factor_value = Decimal(str(factor.numeric_value))
                
                if factor.factor_type == 'discount' and factor_value < 1:
                    discount_amount += base_premium * (Decimal('1.0') - factor_value)
                elif factor.factor_type == 'loading' and factor_value > 1:
                    surcharge_amount += base_premium * (factor_value - Decimal('1.0'))
                else:
                    total_factor *= factor_value
        
        # Calculate final amounts
        adjusted_premium = base_premium * total_factor
        fees_amount = adjusted_premium * Decimal('0.05')  # 5% fees
        tax_amount = (adjusted_premium + fees_amount - discount_amount + surcharge_amount) * Decimal('0.15')  # 15% VAT
        total_premium = adjusted_premium + fees_amount + surcharge_amount - discount_amount + tax_amount
        
        return {
            'base_premium': base_premium,
            'discount_amount': discount_amount,
            'surcharge_amount': surcharge_amount,
            'fees_amount': fees_amount,
            'tax_amount': tax_amount,
            'total_premium': total_premium
        }

    async def _apply_override_factors(self, quotation_id: UUID, 
                                    override_factors: Dict[str, Any]) -> None:
        """Apply override factors to quotation"""
        for key, value in override_factors.items():
            await self.factor_service.upsert_factor(
                quotation_id=quotation_id,
                key=key,
                value=value,
                factor_type='override'
            )

    async def _handle_status_change(self, quotation_id: UUID, new_status: QuotationStatus,
                                   updated_by: UUID = None) -> None:
        """Handle business logic triggered by status changes"""
        if new_status == QuotationStatus.APPROVED:
            # Set auto-expiry date
            await self._set_auto_expiry(quotation_id)
            
        elif new_status == QuotationStatus.CONVERTED:
            # Trigger policy creation workflow
            await self._trigger_policy_creation(quotation_id, updated_by)
            
        elif new_status == QuotationStatus.EXPIRED:
            # Send expiry notification
            await self._send_expiry_notification(quotation_id)

    async def _set_auto_expiry(self, quotation_id: UUID) -> None:
        """Set automatic expiry date for approved quotation"""
        expiry_date = datetime.utcnow() + timedelta(days=30)  # 30 days validity
        
        quotation = self.quotation_repo.get(quotation_id)
        if quotation:
            quotation.auto_expire_at = expiry_date
            self.db.commit()

    async def _trigger_policy_creation(self, quotation_id: UUID, user_id: UUID = None) -> None:
        """Trigger policy creation workflow"""
        # This would integrate with policy management service
        logger.info(f"Triggering policy creation for quotation {quotation_id}")
        
        # Log workflow event
        await self.workflow_service.log_event(
            quotation_id=quotation_id,
            event="policy_creation_triggered",
            notes="Policy creation workflow initiated",
            created_by=user_id
        )

    async def _send_expiry_notification(self, quotation_id: UUID) -> None:
        """Send quotation expiry notification"""
        # This would integrate with notification service
        logger.info(f"Sending expiry notification for quotation {quotation_id}")

    async def _validate_quotation_update_data(self, quotation_data: QuotationUpdate) -> None:
        """Validate quotation update data"""
        # Additional business validations for updates
        if quotation_data.quote_expires_at:
            if quotation_data.quote_expires_at <= datetime.utcnow():
                raise ValidationError("Expiry date cannot be in the past")

    async def _validate_items_data(self, items_data: List[Dict]) -> None:
        """Validate items data for creation"""
        if not items_data:
            raise ValidationError("At least one coverage item is required")
        
        # Validate each item has required fields
        for item in items_data:
            if not item.get('coverage_name') and not item.get('coverage_name_ar'):
                raise ValidationError("Coverage name is required for all items")
