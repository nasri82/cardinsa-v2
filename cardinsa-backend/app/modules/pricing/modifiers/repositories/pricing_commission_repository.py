# app/modules/pricing/modifiers/repositories/pricing_commission_repository.py

from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, or_, case, extract
from uuid import UUID
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal

from app.modules.pricing.modifiers.models.pricing_commission_model import PricingCommission
from app.modules.pricing.modifiers.schemas.pricing_commission_schema import (
    PricingCommissionCreate,
    PricingCommissionUpdate,
)
from app.core.exceptions import NotFoundError, ValidationError

class PricingCommissionRepository:
    """Enhanced repository for commission management with agent hierarchy support"""
    
    # ==================== BASIC CRUD ====================
    
    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        channel: Optional[str] = None,
        is_active: Optional[bool] = None,
        commission_type: Optional[str] = None
    ) -> List[PricingCommission]:
        """Get all commissions with filtering"""
        query = db.query(PricingCommission)
        
        if channel:
            query = query.filter(PricingCommission.channel == channel)
        if is_active is not None:
            query = query.filter(PricingCommission.is_active == is_active)
        if commission_type:
            query = query.filter(PricingCommission.commission_type == commission_type)
        
        return query.offset(skip).limit(limit).all()
    
    def get_by_id(self, db: Session, id: UUID) -> Optional[PricingCommission]:
        """Get commission by ID"""
        return db.query(PricingCommission).filter(PricingCommission.id == id).first()
    
    def get_by_channel(self, db: Session, channel: str) -> Optional[PricingCommission]:
        """Get active commission by channel"""
        return db.query(PricingCommission).filter(
            and_(
                PricingCommission.channel == channel,
                PricingCommission.is_active == True
            )
        ).first()
    
    def create(self, db: Session, data: PricingCommissionCreate) -> PricingCommission:
        """Create new commission with validation"""
        # Validate commission value ranges
        if data.commission_type == "percentage" and data.value > 100:
            raise ValidationError("Commission percentage cannot exceed 100%")
        
        # Check for duplicate active commission for same channel
        existing = self.get_by_channel(db, data.channel)
        if existing and data.is_active:
            raise ValidationError(f"Active commission already exists for channel: {data.channel}")
        
        obj = PricingCommission(**data.dict())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
    
    def update(
        self,
        db: Session,
        db_obj: PricingCommission,
        data: PricingCommissionUpdate
    ) -> PricingCommission:
        """Update commission with validation"""
        update_data = data.dict(exclude_unset=True)
        
        # Validate percentage if updating
        if "commission_type" in update_data or "value" in update_data:
            commission_type = update_data.get("commission_type", db_obj.commission_type)
            value = update_data.get("value", db_obj.value)
            
            if commission_type == "percentage" and value > 100:
                raise ValidationError("Commission percentage cannot exceed 100%")
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: UUID) -> bool:
        """Soft delete commission"""
        obj = self.get_by_id(db, id)
        if obj:
            obj.is_active = False
            obj.deleted_at = datetime.utcnow()
            db.commit()
            return True
        return False
    
    # ==================== AGENT HIERARCHY MANAGEMENT ====================
    
    def get_commissions_by_hierarchy(
        self,
        db: Session,
        hierarchy_level: str
    ) -> List[Dict[str, Any]]:
        """Get commission structures by agent hierarchy level"""
        query = db.query(
            PricingCommission.channel,
            PricingCommission.commission_type,
            PricingCommission.value,
            func.count(PricingCommission.id).label("count")
        ).filter(
            PricingCommission.is_active == True
        ).group_by(
            PricingCommission.channel,
            PricingCommission.commission_type,
            PricingCommission.value
        )
        
        # Map hierarchy levels to channels
        hierarchy_map = {
            "direct": ["direct_sales", "online"],
            "agent": ["agent", "broker"],
            "partner": ["partner", "affiliate"],
            "corporate": ["corporate", "b2b"]
        }
        
        if hierarchy_level in hierarchy_map:
            channels = hierarchy_map[hierarchy_level]
            query = query.filter(PricingCommission.channel.in_(channels))
        
        results = query.all()
        
        return [
            {
                "channel": r.channel,
                "commission_type": r.commission_type,
                "value": float(r.value),
                "active_configs": r.count,
                "hierarchy_level": hierarchy_level
            }
            for r in results
        ]
    
    def calculate_multi_tier_commission(
        self,
        db: Session,
        base_amount: Decimal,
        channel_hierarchy: List[str]
    ) -> Dict[str, Decimal]:
        """Calculate commission for multi-tier agent structure"""
        commissions = {}
        remaining_amount = base_amount
        
        for i, channel in enumerate(channel_hierarchy):
            commission = self.get_by_channel(db, channel)
            
            if commission and commission.is_active:
                if commission.commission_type == "percentage":
                    comm_amount = remaining_amount * (commission.value / 100)
                else:  # fixed
                    comm_amount = min(commission.value, remaining_amount)
                
                commissions[f"tier_{i+1}_{channel}"] = comm_amount
                remaining_amount -= comm_amount
                
                if remaining_amount <= 0:
                    break
        
        commissions["total_commission"] = base_amount - remaining_amount
        commissions["net_amount"] = remaining_amount
        
        return commissions
    
    # ==================== COMMISSION CALCULATION ====================
    
    def calculate_commission(
        self,
        db: Session,
        channel: str,
        base_amount: Decimal,
        policy_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculate commission for a given channel and amount"""
        commission = self.get_by_channel(db, channel)
        
        if not commission:
            return {
                "commission_amount": Decimal("0"),
                "net_amount": base_amount,
                "commission_rate": Decimal("0"),
                "channel": channel,
                "error": "No active commission found"
            }
        
        if commission.commission_type == "percentage":
            commission_amount = base_amount * (commission.value / 100)
            rate = commission.value
        else:  # fixed
            commission_amount = commission.value
            rate = (commission.value / base_amount * 100) if base_amount > 0 else Decimal("0")
        
        # Apply policy-specific adjustments
        if policy_type:
            adjustment = self._get_policy_adjustment(policy_type)
            commission_amount = commission_amount * adjustment
        
        return {
            "commission_amount": commission_amount,
            "net_amount": base_amount - commission_amount,
            "commission_rate": rate,
            "commission_type": commission.commission_type,
            "channel": channel,
            "currency": commission.currency,
            "commission_id": str(commission.id)
        }
    
    def _get_policy_adjustment(self, policy_type: str) -> Decimal:
        """Get policy-specific commission adjustments"""
        adjustments = {
            "life": Decimal("1.2"),      # 20% higher
            "motor": Decimal("1.0"),     # standard
            "health": Decimal("0.9"),    # 10% lower
            "property": Decimal("1.1"),  # 10% higher
            "travel": Decimal("0.8")     # 20% lower
        }
        return adjustments.get(policy_type.lower(), Decimal("1.0"))
    
    # ==================== BULK OPERATIONS ====================
    
    def bulk_create(
        self,
        db: Session,
        commissions: List[PricingCommissionCreate]
    ) -> List[PricingCommission]:
        """Bulk create commissions"""
        created = []
        
        for commission_data in commissions:
            # Deactivate existing for same channel if creating active
            if commission_data.is_active:
                existing = self.get_by_channel(db, commission_data.channel)
                if existing:
                    existing.is_active = False
            
            obj = PricingCommission(**commission_data.dict())
            db.add(obj)
            created.append(obj)
        
        db.commit()
        for obj in created:
            db.refresh(obj)
        
        return created
    
    def bulk_update_by_channel(
        self,
        db: Session,
        channel_updates: Dict[str, Decimal]
    ) -> int:
        """Bulk update commission values by channel"""
        updated_count = 0
        
        for channel, new_value in channel_updates.items():
            commission = self.get_by_channel(db, channel)
            if commission:
                commission.value = new_value
                commission.updated_at = datetime.utcnow()
                updated_count += 1
        
        db.commit()
        return updated_count
    
    # ==================== PERFORMANCE ANALYTICS ====================
    
    def get_commission_statistics(
        self,
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get commission statistics and analytics"""
        query = db.query(
            func.count(PricingCommission.id).label("total_configs"),
            func.count(case((PricingCommission.is_active == True, 1))).label("active_configs"),
            func.avg(case((PricingCommission.commission_type == "percentage", PricingCommission.value))).label("avg_percentage"),
            func.avg(case((PricingCommission.commission_type == "fixed", PricingCommission.value))).label("avg_fixed"),
            func.min(PricingCommission.value).label("min_value"),
            func.max(PricingCommission.value).label("max_value")
        )
        
        if start_date:
            query = query.filter(PricingCommission.created_at >= start_date)
        if end_date:
            query = query.filter(PricingCommission.created_at <= end_date)
        
        stats = query.first()
        
        # Get distribution by channel
        channel_dist = db.query(
            PricingCommission.channel,
            func.count(PricingCommission.id).label("count"),
            func.avg(PricingCommission.value).label("avg_value")
        ).filter(
            PricingCommission.is_active == True
        ).group_by(
            PricingCommission.channel
        ).all()
        
        return {
            "total_configurations": stats.total_configs or 0,
            "active_configurations": stats.active_configs or 0,
            "average_percentage_rate": float(stats.avg_percentage or 0),
            "average_fixed_amount": float(stats.avg_fixed or 0),
            "min_commission_value": float(stats.min_value or 0),
            "max_commission_value": float(stats.max_value or 0),
            "channel_distribution": [
                {
                    "channel": ch.channel,
                    "count": ch.count,
                    "average_value": float(ch.avg_value)
                }
                for ch in channel_dist
            ]
        }
    
    def get_commission_trends(
        self,
        db: Session,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get commission configuration trends over time"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        query = db.query(
            func.date_trunc('day', PricingCommission.created_at).label('date'),
            PricingCommission.channel,
            func.count(PricingCommission.id).label('changes'),
            func.avg(PricingCommission.value).label('avg_value')
        ).filter(
            PricingCommission.created_at >= start_date
        ).group_by(
            func.date_trunc('day', PricingCommission.created_at),
            PricingCommission.channel
        ).order_by('date')
        
        results = query.all()
        
        return [
            {
                "date": r.date.strftime("%Y-%m-%d"),
                "channel": r.channel,
                "changes": r.changes,
                "average_value": float(r.avg_value)
            }
            for r in results
        ]
    
    # ==================== VALIDATION & COMPLIANCE ====================
    
    def validate_commission_limits(
        self,
        db: Session,
        channel: str,
        value: Decimal,
        commission_type: str
    ) -> Tuple[bool, Optional[str]]:
        """Validate commission against regulatory limits"""
        # Define regulatory limits by channel and type
        limits = {
            "broker": {"percentage": 35, "fixed": 10000},
            "agent": {"percentage": 25, "fixed": 5000},
            "partner": {"percentage": 20, "fixed": 3000},
            "direct_sales": {"percentage": 15, "fixed": 2000},
            "online": {"percentage": 10, "fixed": 1000}
        }
        
        channel_limits = limits.get(channel, {"percentage": 30, "fixed": 5000})
        
        if commission_type == "percentage":
            if value > channel_limits["percentage"]:
                return False, f"Commission exceeds regulatory limit of {channel_limits['percentage']}% for {channel}"
        else:  # fixed
            if value > channel_limits["fixed"]:
                return False, f"Fixed commission exceeds limit of {channel_limits['fixed']} for {channel}"
        
        return True, None
    
    def get_compliance_report(
        self,
        db: Session
    ) -> Dict[str, Any]:
        """Generate commission compliance report"""
        all_commissions = db.query(PricingCommission).filter(
            PricingCommission.is_active == True
        ).all()
        
        violations = []
        compliant = []
        
        for comm in all_commissions:
            is_valid, error = self.validate_commission_limits(
                db, comm.channel, comm.value, comm.commission_type
            )
            
            if is_valid:
                compliant.append(comm)
            else:
                violations.append({
                    "commission_id": str(comm.id),
                    "channel": comm.channel,
                    "value": float(comm.value),
                    "type": comm.commission_type,
                    "violation": error
                })
        
        return {
            "total_active": len(all_commissions),
            "compliant_count": len(compliant),
            "violation_count": len(violations),
            "compliance_rate": (len(compliant) / len(all_commissions) * 100) if all_commissions else 100,
            "violations": violations,
            "report_date": datetime.utcnow().isoformat(),
            "status": "COMPLIANT" if not violations else "VIOLATIONS_FOUND"
        }


# Create singleton instance
commission_repository = PricingCommissionRepository()