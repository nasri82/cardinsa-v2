# app/modules/pricing/modifiers/repositories/pricing_industry_adjustment_repository.py

from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, or_, case, text
from uuid import UUID
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
import json

from app.modules.pricing.modifiers.models.pricing_industry_adjustment_model import PricingIndustryAdjustment
from app.modules.pricing.modifiers.schemas.pricing_industry_adjustment_schema import (
    PricingIndustryAdjustmentCreate,
    PricingIndustryAdjustmentUpdate,
)
from app.core.exceptions import NotFoundError, ValidationError

class PricingIndustryAdjustmentRepository:
    """Enhanced repository for industry risk adjustments with NAICS support"""
    
    # ==================== BASIC CRUD ====================
    
    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        min_factor: Optional[Decimal] = None,
        max_factor: Optional[Decimal] = None
    ) -> List[PricingIndustryAdjustment]:
        """Get all industry adjustments with filtering"""
        query = db.query(PricingIndustryAdjustment)
        
        if is_active is not None:
            query = query.filter(PricingIndustryAdjustment.is_active == is_active)
        if min_factor is not None:
            query = query.filter(PricingIndustryAdjustment.adjustment_factor >= min_factor)
        if max_factor is not None:
            query = query.filter(PricingIndustryAdjustment.adjustment_factor <= max_factor)
        
        return query.offset(skip).limit(limit).all()
    
    def get_by_id(self, db: Session, id: UUID) -> Optional[PricingIndustryAdjustment]:
        """Get industry adjustment by ID"""
        return db.query(PricingIndustryAdjustment).filter(
            PricingIndustryAdjustment.id == id
        ).first()
    
    def get_by_industry_code(
        self,
        db: Session,
        industry_code: str
    ) -> Optional[PricingIndustryAdjustment]:
        """Get active adjustment by industry code"""
        return db.query(PricingIndustryAdjustment).filter(
            and_(
                PricingIndustryAdjustment.industry_code == industry_code,
                PricingIndustryAdjustment.is_active == True
            )
        ).first()
    
    def create(
        self,
        db: Session,
        data: PricingIndustryAdjustmentCreate
    ) -> PricingIndustryAdjustment:
        """Create new industry adjustment with validation"""
        # Validate adjustment factor range (0.5 to 3.0 = -50% to +200%)
        if data.adjustment_factor < Decimal("0.5") or data.adjustment_factor > Decimal("3.0"):
            raise ValidationError("Adjustment factor must be between 0.5 and 3.0")
        
        # Check for duplicate active adjustment for same industry
        existing = self.get_by_industry_code(db, data.industry_code)
        if existing and data.is_active:
            raise ValidationError(f"Active adjustment already exists for industry: {data.industry_code}")
        
        # Validate NAICS code format if applicable
        if data.industry_code and not self._validate_naics_code(data.industry_code):
            raise ValidationError(f"Invalid NAICS code format: {data.industry_code}")
        
        obj = PricingIndustryAdjustment(**data.dict())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
    
    def update(
        self,
        db: Session,
        db_obj: PricingIndustryAdjustment,
        data: PricingIndustryAdjustmentUpdate
    ) -> PricingIndustryAdjustment:
        """Update industry adjustment with validation"""
        update_data = data.dict(exclude_unset=True)
        
        # Validate adjustment factor if updating
        if "adjustment_factor" in update_data:
            factor = update_data["adjustment_factor"]
            if factor < Decimal("0.5") or factor > Decimal("3.0"):
                raise ValidationError("Adjustment factor must be between 0.5 and 3.0")
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: UUID) -> bool:
        """Soft delete industry adjustment"""
        obj = self.get_by_id(db, id)
        if obj:
            obj.is_active = False
            obj.deleted_at = datetime.utcnow()
            db.commit()
            return True
        return False
    
    # ==================== NAICS CODE MANAGEMENT ====================
    
    def _validate_naics_code(self, code: str) -> bool:
        """Validate NAICS code format (2-6 digits)"""
        if not code.isdigit():
            return False
        return 2 <= len(code) <= 6
    
    def get_by_naics_hierarchy(
        self,
        db: Session,
        naics_code: str
    ) -> Optional[PricingIndustryAdjustment]:
        """Get adjustment by NAICS code, checking hierarchy (6→4→3→2 digits)"""
        if not self._validate_naics_code(naics_code):
            return None
        
        # Try exact match first
        adjustment = self.get_by_industry_code(db, naics_code)
        if adjustment:
            return adjustment
        
        # Try broader categories (6-digit → 4-digit → 3-digit → 2-digit)
        for length in [4, 3, 2]:
            if len(naics_code) > length:
                broader_code = naics_code[:length]
                adjustment = self.get_by_industry_code(db, broader_code)
                if adjustment:
                    return adjustment
        
        return None
    
    def import_naics_mappings(
        self,
        db: Session,
        mappings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Import NAICS code mappings in bulk"""
        created = 0
        updated = 0
        errors = []
        
        for mapping in mappings:
            try:
                code = mapping.get("industry_code")
                factor = Decimal(str(mapping.get("adjustment_factor", 1.0)))
                description = mapping.get("description", "")
                
                existing = self.get_by_industry_code(db, code)
                
                if existing:
                    existing.adjustment_factor = factor
                    existing.description = description
                    existing.updated_at = datetime.utcnow()
                    updated += 1
                else:
                    obj = PricingIndustryAdjustment(
                        industry_code=code,
                        adjustment_factor=factor,
                        description=description,
                        is_active=True
                    )
                    db.add(obj)
                    created += 1
                    
            except Exception as e:
                errors.append({
                    "code": mapping.get("industry_code"),
                    "error": str(e)
                })
        
        db.commit()
        
        return {
            "created": created,
            "updated": updated,
            "errors": errors,
            "total_processed": created + updated
        }
    
    # ==================== RISK CALCULATION ====================
    
    def calculate_industry_risk(
        self,
        db: Session,
        industry_code: str,
        base_premium: Decimal,
        employee_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """Calculate risk-adjusted premium for industry"""
        adjustment = self.get_by_naics_hierarchy(db, industry_code)
        
        if not adjustment:
            return {
                "base_premium": base_premium,
                "adjusted_premium": base_premium,
                "adjustment_factor": Decimal("1.0"),
                "risk_level": "STANDARD",
                "industry_code": industry_code,
                "adjustment_applied": False
            }
        
        # Apply base industry adjustment
        adjusted_premium = base_premium * adjustment.adjustment_factor
        
        # Apply employee count modifier (larger companies get slight discount)
        if employee_count:
            if employee_count > 1000:
                adjusted_premium *= Decimal("0.95")  # 5% discount
            elif employee_count > 500:
                adjusted_premium *= Decimal("0.97")  # 3% discount
            elif employee_count < 10:
                adjusted_premium *= Decimal("1.05")  # 5% surcharge for very small
        
        # Determine risk level
        risk_level = self._determine_risk_level(adjustment.adjustment_factor)
        
        return {
            "base_premium": base_premium,
            "adjusted_premium": adjusted_premium,
            "adjustment_factor": adjustment.adjustment_factor,
            "risk_level": risk_level,
            "industry_code": industry_code,
            "industry_description": adjustment.description,
            "employee_count_modifier": employee_count is not None,
            "adjustment_applied": True,
            "adjustment_id": str(adjustment.id)
        }
    
    def _determine_risk_level(self, factor: Decimal) -> str:
        """Determine risk level based on adjustment factor"""
        if factor <= Decimal("0.8"):
            return "LOW"
        elif factor <= Decimal("1.0"):
            return "STANDARD"
        elif factor <= Decimal("1.5"):
            return "MODERATE"
        elif factor <= Decimal("2.0"):
            return "HIGH"
        else:
            return "VERY_HIGH"
    
    def calculate_multi_location_risk(
        self,
        db: Session,
        locations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate combined risk for multiple business locations"""
        total_exposure = Decimal("0")
        weighted_factor = Decimal("0")
        location_risks = []
        
        for location in locations:
            industry_code = location.get("industry_code")
            exposure = Decimal(str(location.get("exposure", 0)))
            employees = location.get("employees")
            
            risk = self.calculate_industry_risk(
                db, industry_code, exposure, employees
            )
            
            location_risks.append({
                "location": location.get("name", "Unknown"),
                "industry_code": industry_code,
                "exposure": exposure,
                "adjusted_exposure": risk["adjusted_premium"],
                "risk_level": risk["risk_level"]
            })
            
            total_exposure += exposure
            weighted_factor += risk["adjustment_factor"] * exposure
        
        # Calculate weighted average factor
        avg_factor = weighted_factor / total_exposure if total_exposure > 0 else Decimal("1.0")
        
        return {
            "total_base_exposure": total_exposure,
            "total_adjusted_exposure": sum(l["adjusted_exposure"] for l in location_risks),
            "average_adjustment_factor": avg_factor,
            "overall_risk_level": self._determine_risk_level(avg_factor),
            "location_count": len(locations),
            "location_details": location_risks
        }
    
    # ==================== BULK OPERATIONS ====================
    
    def bulk_create(
        self,
        db: Session,
        adjustments: List[PricingIndustryAdjustmentCreate]
    ) -> List[PricingIndustryAdjustment]:
        """Bulk create industry adjustments"""
        created = []
        
        for adjustment_data in adjustments:
            # Validate each adjustment
            if adjustment_data.adjustment_factor < Decimal("0.5") or \
               adjustment_data.adjustment_factor > Decimal("3.0"):
                continue  # Skip invalid factors
            
            # Deactivate existing for same code if creating active
            if adjustment_data.is_active:
                existing = self.get_by_industry_code(db, adjustment_data.industry_code)
                if existing:
                    existing.is_active = False
            
            obj = PricingIndustryAdjustment(**adjustment_data.dict())
            db.add(obj)
            created.append(obj)
        
        db.commit()
        for obj in created:
            db.refresh(obj)
        
        return created
    
    def bulk_update_factors(
        self,
        db: Session,
        factor_updates: Dict[str, Decimal]
    ) -> int:
        """Bulk update adjustment factors by industry code"""
        updated_count = 0
        
        for industry_code, new_factor in factor_updates.items():
            if new_factor < Decimal("0.5") or new_factor > Decimal("3.0"):
                continue  # Skip invalid factors
            
            adjustment = self.get_by_industry_code(db, industry_code)
            if adjustment:
                adjustment.adjustment_factor = new_factor
                adjustment.updated_at = datetime.utcnow()
                updated_count += 1
        
        db.commit()
        return updated_count
    
    # ==================== ANALYTICS & REPORTING ====================
    
    def get_risk_distribution(
        self,
        db: Session
    ) -> Dict[str, Any]:
        """Get distribution of industries by risk level"""
        all_adjustments = db.query(PricingIndustryAdjustment).filter(
            PricingIndustryAdjustment.is_active == True
        ).all()
        
        distribution = {
            "LOW": 0,
            "STANDARD": 0,
            "MODERATE": 0,
            "HIGH": 0,
            "VERY_HIGH": 0
        }
        
        for adj in all_adjustments:
            risk_level = self._determine_risk_level(adj.adjustment_factor)
            distribution[risk_level] += 1
        
        total = sum(distribution.values())
        
        return {
            "distribution": distribution,
            "percentages": {
                k: (v / total * 100) if total > 0 else 0
                for k, v in distribution.items()
            },
            "total_industries": total,
            "average_factor": db.query(
                func.avg(PricingIndustryAdjustment.adjustment_factor)
            ).filter(
                PricingIndustryAdjustment.is_active == True
            ).scalar() or 1.0
        }
    
    def get_high_risk_industries(
        self,
        db: Session,
        threshold: Decimal = Decimal("1.5")
    ) -> List[Dict[str, Any]]:
        """Get list of high-risk industries"""
        high_risk = db.query(PricingIndustryAdjustment).filter(
            and_(
                PricingIndustryAdjustment.is_active == True,
                PricingIndustryAdjustment.adjustment_factor >= threshold
            )
        ).order_by(
            PricingIndustryAdjustment.adjustment_factor.desc()
        ).all()
        
        return [
            {
                "industry_code": adj.industry_code,
                "adjustment_factor": float(adj.adjustment_factor),
                "risk_level": self._determine_risk_level(adj.adjustment_factor),
                "description": adj.description,
                "premium_increase": f"{(adj.adjustment_factor - 1) * 100:.1f}%"
            }
            for adj in high_risk
        ]
    
    def get_industry_trends(
        self,
        db: Session,
        industry_code: str,
        days: int = 90
    ) -> List[Dict[str, Any]]:
        """Get historical trends for an industry's risk factor"""
        # This would typically query a history table
        # For now, we'll return a simulated trend
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        current = self.get_by_industry_code(db, industry_code)
        if not current:
            return []
        
        # Simulated historical data
        trends = []
        current_factor = float(current.adjustment_factor)
        
        for i in range(0, days, 7):  # Weekly points
            trend_date = start_date + timedelta(days=i)
            # Simulate some variation
            variation = (i % 30 - 15) / 100  # ±15% variation
            factor = current_factor * (1 + variation)
            
            trends.append({
                "date": trend_date.isoformat(),
                "adjustment_factor": factor,
                "risk_level": self._determine_risk_level(Decimal(str(factor)))
            })
        
        return trends
    
    # ==================== EXPORT & REPORTING ====================
    
    def export_industry_matrix(
        self,
        db: Session
    ) -> List[Dict[str, Any]]:
        """Export complete industry risk matrix"""
        all_adjustments = db.query(PricingIndustryAdjustment).filter(
            PricingIndustryAdjustment.is_active == True
        ).order_by(
            PricingIndustryAdjustment.industry_code
        ).all()
        
        matrix = []
        for adj in all_adjustments:
            matrix.append({
                "industry_code": adj.industry_code,
                "description": adj.description,
                "adjustment_factor": float(adj.adjustment_factor),
                "risk_level": self._determine_risk_level(adj.adjustment_factor),
                "premium_impact": f"{(adj.adjustment_factor - 1) * 100:+.1f}%",
                "is_active": adj.is_active,
                "last_updated": adj.updated_at.isoformat() if adj.updated_at else None
            })
        
        return matrix


# Create singleton instance
industry_adjustment_repository = PricingIndustryAdjustmentRepository()