# app/modules/providers/services/provider_network_service.py
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.core.base_service import BaseService
from app.modules.providers.repositories import create_provider_network_repository
from app.modules.providers.models.provider_network_model import ProviderNetwork
from app.modules.providers.schemas.provider_network_schema import (
    ProviderNetworkCreate, 
    ProviderNetworkUpdate,
    ProviderNetworkOut,
    ProviderNetworkSearch
)
from app.core.exceptions import NotFoundError, ValidationError, ConflictError, BusinessLogicError

class ProviderNetworkService(BaseService):
    """Enhanced Provider Network Service with business logic"""
    
    def __init__(self, db: Session):
        repository = create_provider_network_repository(db)
        super().__init__(repository, db)
        self.network_repo = repository
    
    # ==================== CRUD OPERATIONS ====================
    
    def get_provider_network(self, id: UUID) -> ProviderNetworkOut:
        """Get provider network by ID"""
        network = self.get_by_id(id)
        return ProviderNetworkOut.model_validate(network)
    
    def create_provider_network(self, obj_in: ProviderNetworkCreate) -> ProviderNetworkOut:
        """Create new provider network with validation"""
        # Business logic validation
        self._validate_network_create(obj_in)
        
        # Check for duplicate code within company
        if not self.network_repo.validate_code_unique(obj_in.code, obj_in.company_id):
            raise ConflictError(
                f"Network with code '{obj_in.code}' already exists in this company"
            )
        
        # Check for overlapping networks
        overlapping = self.network_repo.find_overlapping_networks(
            coverage_area=obj_in.coverage_area,
            tier=obj_in.tier,
            company_id=obj_in.company_id
        )
        
        if overlapping:
            self.logger.warning(
                f"Creating network that overlaps with existing networks: "
                f"{[n.name for n in overlapping]}"
            )
        
        # Create the network
        network = self.create(obj_in)
        
        self._log_operation(
            "create_provider_network", 
            network.id,
            {
                "code": obj_in.code, 
                "name": obj_in.name, 
                "tier": obj_in.tier,
                "coverage_area": obj_in.coverage_area
            }
        )
        
        return ProviderNetworkOut.model_validate(network)
    
    def update_provider_network(self, id: UUID, obj_in: ProviderNetworkUpdate) -> ProviderNetworkOut:
        """Update provider network with validation"""
        # Get existing network
        existing = self.network_repo.get(id)
        if not existing:
            raise NotFoundError(f"Provider network not found with ID: {id}")
        
        # Business logic validation
        self._validate_network_update(obj_in, existing)
        
        # Check for duplicate code if code is being changed
        if obj_in.code and obj_in.code != existing.code:
            if not self.network_repo.validate_code_unique(
                obj_in.code, 
                existing.company_id, 
                exclude_id=id
            ):
                raise ConflictError(
                    f"Network with code '{obj_in.code}' already exists in this company"
                )
        
        # Update the network
        network = self.update(id, obj_in)
        
        self._log_operation(
            "update_provider_network", 
            id,
            {"updated_fields": obj_in.model_dump(exclude_unset=True)}
        )
        
        return ProviderNetworkOut.model_validate(network)
    
    def delete_provider_network(self, id: UUID) -> bool:
        """Delete provider network with business logic validation"""
        # Get existing network
        existing = self.network_repo.get(id)
        if not existing:
            raise NotFoundError(f"Provider network not found with ID: {id}")
        
        # Business logic validation
        self._validate_network_delete(existing)
        
        # Check if network has active members
        stats = self.network_repo.get_network_statistics(id)
        if stats.get('member_count', 0) > 0:
            raise BusinessLogicError(
                f"Cannot delete network '{existing.name}' because it has {stats['member_count']} active members",
                code="NETWORK_HAS_MEMBERS"
            )
        
        # Delete the network
        success = self.delete(id)
        
        if success:
            self._log_operation(
                "delete_provider_network", 
                id, 
                {"code": existing.code, "name": existing.name}
            )
        
        return success
    
    # ==================== BUSINESS LOGIC METHODS ====================
    
    def search_networks(
        self, 
        search_params: ProviderNetworkSearch,
        skip: int = 0,
        limit: int = 20
    ) -> List[ProviderNetworkOut]:
        """Advanced search for networks"""
        networks = self.network_repo.search_networks(
            search_term=search_params.search,
            company_id=search_params.company_id,
            tier=search_params.tier,
            is_active=search_params.is_active,
            coverage_area=search_params.coverage_area,
            skip=skip,
            limit=limit
        )
        
        return [ProviderNetworkOut.model_validate(n) for n in networks]
    
    def get_active_networks(
        self, 
        company_id: Optional[UUID] = None,
        tier: Optional[str] = None
    ) -> List[ProviderNetworkOut]:
        """Get all active networks"""
        networks = self.network_repo.get_active_networks(
            company_id=company_id,
            tier=tier
        )
        return [ProviderNetworkOut.model_validate(n) for n in networks]
    
    def get_network_by_code(
        self, 
        code: str, 
        company_id: UUID
    ) -> Optional[ProviderNetworkOut]:
        """Get network by unique code within company"""
        network = self.network_repo.get_by_code(code, company_id)
        if network:
            return ProviderNetworkOut.model_validate(network)
        return None
    
    def get_networks_by_coverage_area(
        self, 
        coverage_area: str,
        active_only: bool = True
    ) -> List[ProviderNetworkOut]:
        """Get networks by coverage area"""
        networks = self.network_repo.get_networks_by_coverage_area(
            coverage_area=coverage_area,
            active_only=active_only
        )
        return [ProviderNetworkOut.model_validate(n) for n in networks]
    
    # ==================== ANALYTICS AND STATISTICS ====================
    
    def get_tier_distribution(
        self, 
        company_id: Optional[UUID] = None,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Get network distribution by tier"""
        return self.network_repo.get_tier_distribution(
            company_id=company_id,
            active_only=active_only
        )
    
    def get_coverage_areas_with_counts(
        self, 
        company_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """Get coverage areas with network counts"""
        return self.network_repo.get_coverage_areas_with_counts(company_id=company_id)
    
    def get_network_statistics(self, id: UUID) -> Dict[str, Any]:
        """Get comprehensive network statistics"""
        if not self.network_repo.exists(id):
            raise NotFoundError(f"Provider network not found with ID: {id}")
        
        return self.network_repo.get_network_statistics(id)
    
    def find_overlapping_networks(
        self,
        coverage_area: str,
        tier: str,
        company_id: UUID,
        exclude_id: Optional[UUID] = None
    ) -> List[ProviderNetworkOut]:
        """Find networks with overlapping coverage and tier"""
        overlapping = self.network_repo.find_overlapping_networks(
            coverage_area=coverage_area,
            tier=tier,
            company_id=company_id,
            exclude_id=exclude_id
        )
        return [ProviderNetworkOut.model_validate(n) for n in overlapping]
    
    def get_paginated_networks(
        self,
        page: int = 1,
        page_size: int = 20,
        company_id: Optional[UUID] = None,
        tier: Optional[str] = None,
        is_active: Optional[bool] = None,
        search_term: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get paginated networks with metadata"""
        result = self.network_repo.get_paginated_networks(
            page=page,
            page_size=page_size,
            company_id=company_id,
            tier=tier,
            is_active=is_active,
            search_term=search_term
        )
        
        # Convert items to response schemas
        result["items"] = [ProviderNetworkOut.model_validate(n) for n in result["items"]]
        
        return result
    
    # ==================== BULK OPERATIONS ====================
    
    def bulk_update_status(
        self, 
        network_ids: List[UUID],
        is_active: bool,
        company_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Bulk update network status"""
        if not network_ids:
            raise ValidationError("Network IDs cannot be empty")
        
        # Validate all IDs exist and belong to company if specified
        for network_id in network_ids:
            network = self.network_repo.get(network_id)
            if not network:
                raise NotFoundError(f"Network not found with ID: {network_id}")
            
            if company_id and network.company_id != company_id:
                raise ValidationError(f"Network {network_id} does not belong to specified company")
        
        updated_count = self.network_repo.bulk_update_status(
            network_ids, 
            is_active, 
            company_id
        )
        
        self._log_operation(
            "bulk_update_network_status",
            details={
                "updated_count": updated_count,
                "total_requested": len(network_ids),
                "is_active": is_active,
                "company_id": str(company_id) if company_id else None
            }
        )
        
        return {
            "updated_count": updated_count,
            "total_requested": len(network_ids),
            "success_rate": updated_count / len(network_ids) if network_ids else 0
        }
    
    # ==================== VALIDATION METHODS ====================
    
    def _validate_network_create(self, obj_in: ProviderNetworkCreate) -> None:
        """Validate network creation"""
        self._validate_string_length(obj_in.code, "code", min_length=2, max_length=50)
        self._validate_string_length(obj_in.name, "name", min_length=2, max_length=200)
        
        if obj_in.description and len(obj_in.description) > 1000:
            raise ValidationError("Description cannot exceed 1000 characters")
        
        # Validate tier
        valid_tiers = ["Tier1", "Tier2", "OutOfNetwork", "Premium", "Standard", "Basic"]
        if obj_in.tier not in valid_tiers:
            raise ValidationError(f"Tier must be one of: {', '.join(valid_tiers)}")
        
        if obj_in.coverage_area:
            self._validate_string_length(obj_in.coverage_area, "coverage_area", min_length=2, max_length=100)
    
    def _validate_network_update(self, obj_in: ProviderNetworkUpdate, existing: ProviderNetwork) -> None:
        """Validate network update"""
        if obj_in.code is not None:
            self._validate_string_length(obj_in.code, "code", min_length=2, max_length=50)
        
        if obj_in.name is not None:
            self._validate_string_length(obj_in.name, "name", min_length=2, max_length=200)
        
        if obj_in.description is not None and len(obj_in.description) > 1000:
            raise ValidationError("Description cannot exceed 1000 characters")
        
        # Validate tier if provided
        if obj_in.tier is not None:
            valid_tiers = ["Tier1", "Tier2", "OutOfNetwork", "Premium", "Standard", "Basic"]
            if obj_in.tier not in valid_tiers:
                raise ValidationError(f"Tier must be one of: {', '.join(valid_tiers)}")
        
        if obj_in.coverage_area is not None:
            self._validate_string_length(obj_in.coverage_area, "coverage_area", min_length=2, max_length=100)
    
    def _validate_network_delete(self, existing: ProviderNetwork) -> None:
        """Validate network deletion"""
        # Additional business logic validation can be added here
        pass
    
    # ==================== LIFECYCLE HOOKS ====================
    
    def _post_create_operations(self, entity: ProviderNetwork) -> None:
        """Operations after network creation"""
        # Could trigger events, notifications, etc.
        self.logger.info(f"Provider network created: {entity.code} - {entity.name}")
    
    def _post_update_operations(self, entity: ProviderNetwork) -> None:
        """Operations after network update"""
        # Could trigger events, cache invalidation, etc.
        self.logger.info(f"Provider network updated: {entity.code} - {entity.name}")
    
    def _post_delete_operations(self, entity_id: UUID) -> None:
        """Operations after network deletion"""
        # Could trigger cleanup operations
        self.logger.info(f"Provider network deleted: {entity_id}")


# ==================== SERVICE FACTORY ====================

def create_provider_network_service(db: Session) -> ProviderNetworkService:
    """Create provider network service instance"""
    return ProviderNetworkService(db)


# ==================== LEGACY COMPATIBILITY ====================
# For backward compatibility with existing routes

def get_provider_network(db: Session, id: UUID):
    """Legacy function for existing routes"""
    service = create_provider_network_service(db)
    return service.get_provider_network(id)

def create_provider_network(db: Session, obj_in: ProviderNetworkCreate):
    """Legacy function for existing routes"""
    service = create_provider_network_service(db)
    return service.create_provider_network(obj_in)

def update_provider_network(db: Session, id: UUID, obj_in: ProviderNetworkUpdate):
    """Legacy function for existing routes"""
    service = create_provider_network_service(db)
    return service.update_provider_network(id, obj_in)

def delete_provider_network(db: Session, id: UUID):
    """Legacy function for existing routes"""
    service = create_provider_network_service(db)
    return service.delete_provider_network(id)