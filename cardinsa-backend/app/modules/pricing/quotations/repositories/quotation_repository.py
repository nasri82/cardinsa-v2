# app/modules/pricing/quotations/repositories/quotation_repository.py

from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_

from app.core.base_repository import BaseRepository
from ..models import Quotation
from ..schemas import QuotationCreate, QuotationUpdate, QuotationStatusEnum

class QuotationRepository(BaseRepository):  # ✅ Fixed: No generic parameters
    """
    Repository for quotation-related database operations.
    Provides specialized methods for quotation management.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the quotation repository.
        
        Args:
            db: Database session
        """
        super().__init__(Quotation, db)
    
    # ==================== QUOTATION-SPECIFIC METHODS ====================
    
    def get_by_quote_number(self, quote_number: str) -> Optional[Quotation]:
        """
        Get a quotation by quote number.
        
        Args:
            quote_number: Quote number to search for
            
        Returns:
            Quotation instance or None if not found
        """
        return self.get_by_field("quote_number", quote_number)
    
    def get_by_customer_email(self, customer_email: str) -> List[Quotation]:
        """
        Get all quotations for a customer by email.
        
        Args:
            customer_email: Customer email address
            
        Returns:
            List of quotation instances
        """
        return self.get_multi(filters={"customer_email": customer_email})
    
    def get_by_status(self, status: QuotationStatusEnum) -> List[Quotation]:
        """
        Get all quotations with a specific status.
        
        Args:
            status: Quotation status
            
        Returns:
            List of quotation instances
        """
        return self.get_multi(filters={"status": status.value})
    
    def get_active_quotations(self) -> List[Quotation]:
        """
        Get all active (non-locked, non-expired) quotations.
        
        Returns:
            List of active quotation instances
        """
        return self.get_multi(filters={"is_locked": False})
    
    def get_locked_quotations(self) -> List[Quotation]:
        """
        Get all locked quotations.
        
        Returns:
            List of locked quotation instances
        """
        return self.get_multi(filters={"is_locked": True})
    
    def get_by_assigned_user(self, user_id: UUID) -> List[Quotation]:
        """
        Get all quotations assigned to a specific user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of quotation instances
        """
        return self.get_multi(filters={"assigned_to_user_id": user_id})
    
    def get_expiring_soon(self, days: int = 7) -> List[Quotation]:
        """
        Get quotations expiring within the specified number of days.
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            List of expiring quotation instances
        """
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() + timedelta(days=days)
        
        query = select(self.model).where(
            and_(
                self.model.quote_expires_at <= cutoff_date,
                self.model.quote_expires_at >= datetime.now(),
                self.model.status != QuotationStatusEnum.EXPIRED.value,
                self.model.status != QuotationStatusEnum.CONVERTED.value
            )
        )
        
        return list(self.db.scalars(query))
    
    def search_quotations(
        self, 
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Quotation]:
        """
        Search quotations by customer name, email, or quote number.
        
        Args:
            search_term: Search term
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching quotation instances
        """
        search_fields = ["customer_name", "customer_email", "quote_number"]
        return self.search(search_term, search_fields, skip, limit)
    
    def get_quotations_by_premium_range(
        self,
        min_premium: float,
        max_premium: float
    ) -> List[Quotation]:
        """
        Get quotations within a specific premium range.
        
        Args:
            min_premium: Minimum premium amount
            max_premium: Maximum premium amount
            
        Returns:
            List of quotation instances
        """
        query = select(self.model).where(
            and_(
                self.model.total_premium >= min_premium,
                self.model.total_premium <= max_premium,
                self.model.total_premium.isnot(None)
            )
        )
        
        return list(self.db.scalars(query))
    
    def get_quotations_by_date_range(
        self,
        start_date,
        end_date,
        date_field: str = "created_at"
    ) -> List[Quotation]:
        """
        Get quotations within a specific date range.
        
        Args:
            start_date: Start date
            end_date: End date
            date_field: Date field to filter by (created_at, updated_at, etc.)
            
        Returns:
            List of quotation instances
        """
        if not hasattr(self.model, date_field):
            raise ValueError(f"Invalid date field: {date_field}")
        
        date_column = getattr(self.model, date_field)
        query = select(self.model).where(
            and_(
                date_column >= start_date,
                date_column <= end_date
            )
        )
        
        return list(self.db.scalars(query))
    
    # ==================== STATUS MANAGEMENT ====================
    
    def update_status(self, quotation_id: UUID, new_status: QuotationStatusEnum) -> Optional[Quotation]:
        """
        Update the status of a quotation.
        
        Args:
            quotation_id: Quotation ID
            new_status: New status
            
        Returns:
            Updated quotation instance or None if not found
        """
        return self.update(quotation_id, {"status": new_status.value})
    
    def lock_quotation(self, quotation_id: UUID, lock_reason: str, locked_by: int) -> Optional[Quotation]:
        """
        Lock a quotation.
        
        Args:
            quotation_id: Quotation ID
            lock_reason: Reason for locking
            locked_by: User ID who locked the quotation
            
        Returns:
            Updated quotation instance or None if not found
        """
        from datetime import datetime
        
        return self.update(quotation_id, {
            "is_locked": True,
            "lock_reason": lock_reason,
            "locked_by": locked_by,
            "locked_at": datetime.now()
        })
    
    def unlock_quotation(self, quotation_id: UUID) -> Optional[Quotation]:
        """
        Unlock a quotation.
        
        Args:
            quotation_id: Quotation ID
            
        Returns:
            Updated quotation instance or None if not found
        """
        return self.update(quotation_id, {
            "is_locked": False,
            "lock_reason": None,
            "locked_by": None,
            "locked_at": None
        })
    
    # ==================== STATISTICS AND REPORTING ====================
    
    def get_quotation_stats(self) -> Dict[str, Any]:
        """
        Get quotation statistics.
        
        Returns:
            Dictionary with various statistics
        """
        total_count = self.count()
        active_count = self.count(filters={"is_locked": False})
        locked_count = self.count(filters={"is_locked": True})
        
        # Count by status
        status_counts = {}
        for status in QuotationStatusEnum:
            count = self.count(filters={"status": status.value})
            status_counts[status.value] = count
        
        return {
            "total_quotations": total_count,
            "active_quotations": active_count,
            "locked_quotations": locked_count,
            "status_breakdown": status_counts
        }
    
    def get_recent_quotations(self, days: int = 30, limit: int = 10) -> List[Quotation]:
        """
        Get recently created quotations.
        
        Args:
            days: Number of days to look back
            limit: Maximum number of quotations to return
            
        Returns:
            List of recent quotation instances
        """
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = select(self.model).where(
            self.model.created_at >= cutoff_date
        ).order_by(self.model.created_at.desc()).limit(limit)
        
        return list(self.db.scalars(query))
    
    # ==================== BULK OPERATIONS ====================
    
    def bulk_update_status(self, quotation_ids: List[UUID], new_status: QuotationStatusEnum) -> int:
        """
        Bulk update status for multiple quotations.
        
        Args:
            quotation_ids: List of quotation IDs
            new_status: New status
            
        Returns:
            Number of records updated
        """
        from sqlalchemy import update
        
        query = update(self.model).where(
            self.model.id.in_(quotation_ids)
        ).values(status=new_status.value)
        
        result = self.db.execute(query)
        self.db.commit()
        
        return result.rowcount
    
    def expire_old_quotations(self, days_old: int = 30) -> int:
        """
        Mark old quotations as expired.
        
        Args:
            days_old: Age in days after which quotations should be expired
            
        Returns:
            Number of quotations expired
        """
        from datetime import datetime, timedelta
        from sqlalchemy import update
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        query = update(self.model).where(
            and_(
                self.model.created_at <= cutoff_date,
                self.model.status == QuotationStatusEnum.DRAFT.value
            )
        ).values(status=QuotationStatusEnum.EXPIRED.value)
        
        result = self.db.execute(query)
        self.db.commit()
        
        return result.rowcount