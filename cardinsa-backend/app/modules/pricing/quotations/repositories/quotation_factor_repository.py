# app/modules/pricing/quotations/repositories/quotation_factor_repository.py

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, cast, String
from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from datetime import datetime
import json

from ..models import QuotationFactor
from ..schemas.quotation_factor_schema import FactorType  # Direct import to avoid circular import
from ..schemas import QuotationFactorCreate, QuotationFactorUpdate
from app.core.base_repository import BaseRepository


class QuotationFactorRepository(BaseRepository):  # ✅ Fixed: No generic parameters
    """
    Repository class for QuotationFactor operations
    
    Provides data access methods for pricing factors including
    type-based querying, value parsing, and impact analysis.
    """

    def __init__(self, db: Session):
        super().__init__(QuotationFactor, db)

    # ========== CREATE OPERATIONS ==========

    def create_factor(self, factor_data: QuotationFactorCreate, created_by: UUID = None) -> QuotationFactor:
        """Create a new quotation factor with audit tracking"""
        # Convert Pydantic model to dict
        if hasattr(factor_data, 'model_dump'):
            factor_dict = factor_data.model_dump(exclude_unset=True)
        else:
            factor_dict = factor_data.dict(exclude_unset=True)
        
        factor = QuotationFactor(**factor_dict)
        factor.created_by = created_by
        
        self.db.add(factor)
        self.db.commit()
        self.db.refresh(factor)
        return factor

    def create_numeric_factor(self, quotation_id: UUID, key: str, value: float,
                            factor_type: FactorType = None, impact_description: str = None,
                            created_by: UUID = None) -> QuotationFactor:
        """Create a numeric factor"""
        factor = QuotationFactor(
            quotation_id=quotation_id,
            key=key.lower(),
            value=str(value),
            factor_type=factor_type,
            impact_description=impact_description,
            created_by=created_by
        )
        
        self.db.add(factor)
        self.db.commit()
        self.db.refresh(factor)
        return factor

    def create_boolean_factor(self, quotation_id: UUID, key: str, value: bool,
                            factor_type: FactorType = None, impact_description: str = None,
                            created_by: UUID = None) -> QuotationFactor:
        """Create a boolean factor"""
        factor = QuotationFactor(
            quotation_id=quotation_id,
            key=key.lower(),
            value=str(value).lower(),
            factor_type=factor_type,
            impact_description=impact_description,
            created_by=created_by
        )
        
        self.db.add(factor)
        self.db.commit()
        self.db.refresh(factor)
        return factor

    def create_complex_factor(self, quotation_id: UUID, key: str, 
                            value: Union[Dict[str, Any], List[Any]],
                            factor_type: FactorType = None, impact_description: str = None,
                            created_by: UUID = None) -> QuotationFactor:
        """Create a complex factor with JSON value"""
        factor = QuotationFactor(
            quotation_id=quotation_id,
            key=key.lower(),
            value=json.dumps(value),
            factor_type=factor_type,
            impact_description=impact_description,
            created_by=created_by
        )
        
        self.db.add(factor)
        self.db.commit()
        self.db.refresh(factor)
        return factor

    def create_bulk_factors(self, factors_data: List[QuotationFactorCreate],
                          created_by: UUID = None) -> List[QuotationFactor]:
        """Create multiple factors in bulk"""
        created_factors = []
        
        for factor_data in factors_data:
            factor = self.create_factor(factor_data, created_by)
            created_factors.append(factor)
        
        return created_factors

    # ========== READ OPERATIONS ==========

    def get_by_quotation(self, quotation_id: UUID, active_only: bool = True) -> List[QuotationFactor]:
        """Get all factors for a quotation"""
        query = self.db.query(self.model).filter(
            self.model.quotation_id == quotation_id
        )
        
        if active_only:
            query = query.filter(self.model.archived_at.is_(None))
        
        return query.order_by(asc(self.model.key)).all()

    def get_by_quotation_and_type(self, quotation_id: UUID, 
                                 factor_type: FactorType) -> List[QuotationFactor]:
        """Get factors by quotation and type"""
        return self.db.query(self.model).filter(
            and_(
                self.model.quotation_id == quotation_id,
                self.model.factor_type == factor_type,
                self.model.archived_at.is_(None)
            )
        ).order_by(asc(self.model.key)).all()

    def get_by_key(self, quotation_id: UUID, key: str) -> Optional[QuotationFactor]:
        """Get factor by quotation ID and key"""
        return self.db.query(self.model).filter(
            and_(
                self.model.quotation_id == quotation_id,
                self.model.key == key.lower(),
                self.model.archived_at.is_(None)
            )
        ).first()

    def get_numeric_factors(self, quotation_id: UUID) -> List[QuotationFactor]:
        """Get all numeric factors for a quotation"""
        factors = self.get_by_quotation(quotation_id)
        # Filter for numeric factors (assuming there's an is_numeric property)
        return [factor for factor in factors if self._is_numeric_value(factor.value)]

    def get_factors_by_keys(self, quotation_id: UUID, keys: List[str]) -> List[QuotationFactor]:
        """Get factors by list of keys"""
        normalized_keys = [key.lower() for key in keys]
        return self.db.query(self.model).filter(
            and_(
                self.model.quotation_id == quotation_id,
                self.model.key.in_(normalized_keys),
                self.model.archived_at.is_(None)
            )
        ).order_by(asc(self.model.key)).all()

    def search_factors(self, quotation_id: UUID, search_term: str) -> List[QuotationFactor]:
        """Search factors by key, value, or impact description"""
        search_pattern = f"%{search_term}%"
        return self.db.query(self.model).filter(
            and_(
                self.model.quotation_id == quotation_id,
                or_(
                    self.model.key.ilike(search_pattern),
                    self.model.value.ilike(search_pattern),
                    self.model.impact_description.ilike(search_pattern)
                ),
                self.model.archived_at.is_(None)
            )
        ).order_by(asc(self.model.key)).all()

    def get_factors_grouped_by_type(self, quotation_id: UUID) -> Dict[str, List[QuotationFactor]]:
        """Get factors grouped by type"""
        factors = self.get_by_quotation(quotation_id)
        
        grouped = {}
        for factor in factors:
            factor_type = factor.factor_type or 'other'
            if factor_type not in grouped:
                grouped[factor_type] = []
            grouped[factor_type].append(factor)
        
        return grouped

    # ========== UPDATE OPERATIONS ==========

    def update_factor_value(self, factor_id: UUID, value: Any, 
                           impact_description: str = None,
                           updated_by: UUID = None) -> Optional[QuotationFactor]:
        """Update factor value and impact description"""
        factor = self.get(factor_id)
        if not factor:
            return None
        
        # Set value (convert complex types to JSON string)
        if isinstance(value, (dict, list)):
            factor.value = json.dumps(value)
        else:
            factor.value = str(value)
        
        if impact_description is not None:
            factor.impact_description = impact_description
        
        factor.updated_by = updated_by
        self.db.commit()
        return factor

    def update_factor_type(self, factor_id: UUID, factor_type: FactorType,
                          updated_by: UUID = None) -> Optional[QuotationFactor]:
        """Update factor type"""
        factor = self.get(factor_id)
        if not factor:
            return None
        
        factor.factor_type = factor_type
        factor.updated_by = updated_by
        self.db.commit()
        return factor

    def upsert_factor(self, quotation_id: UUID, key: str, value: Any,
                     factor_type: FactorType = None, impact_description: str = None,
                     updated_by: UUID = None) -> QuotationFactor:
        """Insert or update factor by key"""
        existing_factor = self.get_by_key(quotation_id, key)
        
        if existing_factor:
            # Update existing factor
            if isinstance(value, (dict, list)):
                existing_factor.value = json.dumps(value)
            else:
                existing_factor.value = str(value)
                
            if factor_type is not None:
                existing_factor.factor_type = factor_type
            if impact_description is not None:
                existing_factor.impact_description = impact_description
            existing_factor.updated_by = updated_by
            
            self.db.commit()
            return existing_factor
        else:
            # Create new factor
            value_str = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
            
            new_factor = QuotationFactor(
                quotation_id=quotation_id,
                key=key.lower(),
                value=value_str,
                factor_type=factor_type,
                impact_description=impact_description,
                created_by=updated_by
            )
            
            self.db.add(new_factor)
            self.db.commit()
            self.db.refresh(new_factor)
            return new_factor

    def bulk_upsert_factors(self, quotation_id: UUID, factors: Dict[str, Any],
                           factor_type: FactorType = None,
                           updated_by: UUID = None) -> List[QuotationFactor]:
        """Bulk upsert factors"""
        upserted_factors = []
        
        for key, value in factors.items():
            factor = self.upsert_factor(
                quotation_id=quotation_id,
                key=key,
                value=value,
                factor_type=factor_type,
                updated_by=updated_by
            )
            upserted_factors.append(factor)
        
        return upserted_factors

    # ========== DELETE OPERATIONS ==========

    def soft_delete(self, factor_id: UUID, deleted_by: UUID = None) -> bool:
        """Soft delete factor by setting archived_at"""
        factor = self.get(factor_id)
        if not factor:
            return False
        
        factor.archived_at = datetime.utcnow()
        factor.updated_by = deleted_by
        self.db.commit()
        return True

    def delete_by_key(self, quotation_id: UUID, key: str) -> bool:
        """Delete factor by key"""
        factor = self.get_by_key(quotation_id, key)
        if not factor:
            return False
        
        self.db.delete(factor)
        self.db.commit()
        return True

    def delete_by_type(self, quotation_id: UUID, factor_type: FactorType) -> int:
        """Delete all factors of a specific type"""
        factors = self.get_by_quotation_and_type(quotation_id, factor_type)
        
        for factor in factors:
            factor.archived_at = datetime.utcnow()
        
        self.db.commit()
        return len(factors)

    def delete_all_by_quotation(self, quotation_id: UUID, 
                               hard_delete: bool = False) -> int:
        """Delete all factors for a quotation"""
        if hard_delete:
            count = self.db.query(self.model).filter(
                self.model.quotation_id == quotation_id
            ).count()
            
            self.db.query(self.model).filter(
                self.model.quotation_id == quotation_id
            ).delete()
        else:
            factors = self.db.query(self.model).filter(
                and_(
                    self.model.quotation_id == quotation_id,
                    self.model.archived_at.is_(None)
                )
            ).all()
            
            count = len(factors)
            for factor in factors:
                factor.archived_at = datetime.utcnow()
        
        self.db.commit()
        return count

    # ========== ANALYSIS OPERATIONS ==========

    def get_factor_impact_analysis(self, quotation_id: UUID) -> List[Dict[str, Any]]:
        """Analyze factor impacts on pricing"""
        factors = self.get_by_quotation(quotation_id)
        
        analysis = []
        for factor in factors:
            parsed_value = self._parse_factor_value(factor.value)
            is_numeric = self._is_numeric_value(factor.value)
            numeric_value = self._get_numeric_value(factor.value) if is_numeric else None
            
            impact_data = {
                'factor_id': factor.id,
                'key': factor.key,
                'value': factor.value,
                'parsed_value': parsed_value,
                'factor_type': factor.factor_type,
                'impact_description': factor.impact_description,
                'is_numeric': is_numeric,
                'numeric_value': numeric_value
            }
            
            # Calculate impact if numeric
            if is_numeric and numeric_value is not None:
                if numeric_value > 1:
                    impact_data['impact_type'] = 'loading'
                    impact_data['impact_percentage'] = (numeric_value - 1) * 100
                elif numeric_value < 1:
                    impact_data['impact_type'] = 'discount'
                    impact_data['impact_percentage'] = (1 - numeric_value) * 100
                else:
                    impact_data['impact_type'] = 'neutral'
                    impact_data['impact_percentage'] = 0
            else:
                impact_data['impact_type'] = 'non_numeric'
                impact_data['impact_percentage'] = None
            
            analysis.append(impact_data)
        
        return analysis

    def get_factors_summary(self, quotation_id: UUID) -> Dict[str, Any]:
        """Get summary statistics for quotation factors"""
        factors = self.get_by_quotation(quotation_id)
        
        total_factors = len(factors)
        numeric_factors = len([f for f in factors if self._is_numeric_value(f.value)])
        
        # Count by type
        type_counts = {}
        for factor in factors:
            factor_type = factor.factor_type or 'other'
            type_counts[factor_type] = type_counts.get(factor_type, 0) + 1
        
        # Calculate numeric statistics
        numeric_values = []
        for factor in factors:
            numeric_val = self._get_numeric_value(factor.value)
            if numeric_val is not None:
                numeric_values.append(numeric_val)
        
        return {
            'total_factors': total_factors,
            'numeric_factors': numeric_factors,
            'non_numeric_factors': total_factors - numeric_factors,
            'factors_by_type': type_counts,
            'numeric_statistics': {
                'count': len(numeric_values),
                'min': min(numeric_values) if numeric_values else None,
                'max': max(numeric_values) if numeric_values else None,
                'avg': sum(numeric_values) / len(numeric_values) if numeric_values else None
            },
            'factors_with_impact_description': len([f for f in factors if f.impact_description])
        }

    def validate_factors(self, quotation_id: UUID) -> Dict[str, Any]:
        """Validate factors and return validation results"""
        factors = self.get_by_quotation(quotation_id)
        
        validation_errors = []
        warnings = []
        suggestions = []
        
        # Check for duplicate keys
        keys = [f.key for f in factors]
        if len(keys) != len(set(keys)):
            duplicates = [key for key in set(keys) if keys.count(key) > 1]
            validation_errors.append(f"Duplicate factor keys found: {duplicates}")
        
        # Validate factors
        for factor in factors:
            if factor.value and not factor.value.strip():
                validation_errors.append(f"Empty value for factor '{factor.key}'")
            
            # Check for potentially numeric values that aren't parsed correctly
            if not self._is_numeric_value(factor.value) and factor.value:
                try:
                    float(factor.value.replace(',', ''))
                    suggestions.append(f"Factor '{factor.key}' appears to be numeric but not parsed as such")
                except ValueError:
                    pass
            
            # Check for missing impact descriptions
            if not factor.impact_description:
                warnings.append(f"Missing impact description for factor '{factor.key}'")
        
        return {
            'is_valid': len(validation_errors) == 0,
            'validation_errors': validation_errors,
            'warnings': warnings,
            'suggested_corrections': suggestions
        }

    # ========== HELPER METHODS ==========

    def _is_numeric_value(self, value: str) -> bool:
        """Check if a string value represents a number"""
        if not value:
            return False
        try:
            float(value.replace(',', ''))
            return True
        except ValueError:
            return False

    def _get_numeric_value(self, value: str) -> Optional[float]:
        """Get numeric value from string, return None if not numeric"""
        if not self._is_numeric_value(value):
            return None
        try:
            return float(value.replace(',', ''))
        except ValueError:
            return None

    def _parse_factor_value(self, value: str) -> Any:
        """Parse factor value to appropriate type"""
        if not value:
            return None
        
        # Try to parse as JSON first (for complex values)
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass
        
        # Try to parse as number
        if self._is_numeric_value(value):
            return self._get_numeric_value(value)
        
        # Try to parse as boolean
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Return as string
        return value

    def get_factor_keys(self, quotation_id: UUID) -> List[str]:
        """Get list of all factor keys for a quotation"""
        result = self.db.query(self.model.key).filter(
            and_(
                self.model.quotation_id == quotation_id,
                self.model.archived_at.is_(None)
            )
        ).order_by(asc(self.model.key)).all()
        
        return [row.key for row in result]

    def factor_exists(self, quotation_id: UUID, key: str) -> bool:
        """Check if a factor with the given key exists"""
        return self.db.query(self.model).filter(
            and_(
                self.model.quotation_id == quotation_id,
                self.model.key == key.lower(),
                self.model.archived_at.is_(None)
            )
        ).first() is not None

    def get_factors_count_by_quotation(self, quotation_id: UUID, active_only: bool = True) -> int:
        """Get count of factors for a quotation"""
        query = self.db.query(func.count(self.model.id)).filter(
            self.model.quotation_id == quotation_id
        )
        
        if active_only:
            query = query.filter(self.model.archived_at.is_(None))
        
        return query.scalar()

    def duplicate_factors_to_quotation(self, source_quotation_id: UUID,
                                     target_quotation_id: UUID,
                                     created_by: UUID = None) -> List[QuotationFactor]:
        """Duplicate factors from one quotation to another"""
        source_factors = self.get_by_quotation(source_quotation_id)
        
        duplicated_factors = []
        for source_factor in source_factors:
            # Create new factor with same data
            new_factor = QuotationFactor(
                quotation_id=target_quotation_id,
                key=source_factor.key,
                value=source_factor.value,
                factor_type=source_factor.factor_type,
                impact_description=source_factor.impact_description,
                created_by=created_by
            )
            
            self.db.add(new_factor)
            duplicated_factors.append(new_factor)
        
        self.db.commit()
        return duplicated_factors