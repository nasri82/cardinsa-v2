# =============================================================================
# FILE: app/modules/underwriting/repositories/underwriting_repository.py
# WORLD-CLASS UNDERWRITING REPOSITORY - ENTERPRISE GRADE
# =============================================================================

"""
Underwriting Repository - Enterprise Data Access Layer

Comprehensive repository providing:
- CRUD operations for all underwriting entities
- Advanced query capabilities with filtering
- Performance optimized database operations
- Transaction management and data integrity
- Caching and performance optimization
- Audit trail and change tracking
"""

from typing import Dict, List, Optional, Any, Tuple, Union
from uuid import UUID
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging
from contextlib import contextmanager

from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import and_, or_, not_, func, desc, asc, exists
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.sql import text

# Core imports
from app.core.exceptions import EntityNotFoundError, BusinessLogicError, DatabaseError
from app.core.base_repository import BaseRepository
from app.core.cache import cache_manager
from app.core.logging import get_logger

# Model imports
from app.modules.underwriting.models.underwriting_rule_model import (
    UnderwritingRule, UnderwritingDecision, UnderwritingException
)
from app.modules.underwriting.models.underwriting_profile_model import (
    UnderwritingProfile, UnderwritingAction, UnderwritingDocument, UnderwritingLog
)
from app.modules.underwriting.models.underwriting_application_model import (
    UnderwritingApplication, ApplicationCommunication, ApplicationFollowUp
)
from app.modules.underwriting.models.underwriting_workflow_model import (
    UnderwritingWorkflow, UnderwritingWorkflowStep, WorkflowExecution, WorkflowStepExecution
)

# Schema imports
from app.modules.underwriting.schemas.underwriting_schema import (
    UnderwritingRuleSearchFilters, UnderwritingProfileSearchFilters,
    UnderwritingApplicationSearchFilters
)


# =============================================================================
# UNDERWRITING REPOSITORY
# =============================================================================

class UnderwritingRepository(BaseRepository):
    """
    World-Class Underwriting Repository
    
    Comprehensive data access layer providing:
    - High-performance CRUD operations
    - Advanced filtering and search capabilities
    - Optimized queries with eager loading
    - Transaction management and data integrity
    - Caching and performance optimization
    - Analytics and reporting queries
    """
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.logger = get_logger(__name__)
        self.cache_ttl = 300  # 5 minutes default cache TTL
    
    # =========================================================================
    # UNDERWRITING RULES REPOSITORY
    # =========================================================================
    
    def create_rule(self, rule_data: dict, created_by: UUID) -> UnderwritingRule:
        """Create new underwriting rule"""
        try:
            rule = UnderwritingRule(**rule_data)
            rule.created_by = created_by
            
            self.db.add(rule)
            self.db.commit()
            self.db.refresh(rule)
            
            # Clear cache
            self._clear_rules_cache()
            
            self.logger.info(f"Created underwriting rule: {rule.rule_name} (ID: {rule.id})")
            return rule
            
        except IntegrityError as e:
            self.db.rollback()
            if "duplicate key" in str(e).lower():
                raise BusinessLogicError(f"Rule name '{rule_data.get('rule_name')}' already exists")
            raise DatabaseError(f"Database integrity error: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to create rule: {str(e)}")
    
    def get_rule_by_id(self, rule_id: UUID, include_relationships: bool = False) -> Optional[UnderwritingRule]:
        """Get underwriting rule by ID"""
        try:
            query = self.db.query(UnderwritingRule).filter(
                UnderwritingRule.id == rule_id,
                UnderwritingRule.archived_at.is_(None)
            )
            
            if include_relationships:
                query = query.options(
                    selectinload(UnderwritingRule.decisions),
                    selectinload(UnderwritingRule.exceptions),
                    selectinload(UnderwritingRule.child_rules)
                )
            
            return query.first()
            
        except Exception as e:
            raise DatabaseError(f"Failed to get rule: {str(e)}")
    
    def get_rule_by_name(self, rule_name: str, product_type: str) -> Optional[UnderwritingRule]:
        """Get rule by name and product type"""
        try:
            return self.db.query(UnderwritingRule).filter(
                UnderwritingRule.rule_name == rule_name,
                UnderwritingRule.product_type == product_type,
                UnderwritingRule.archived_at.is_(None)
            ).first()
            
        except Exception as e:
            raise DatabaseError(f"Failed to get rule by name: {str(e)}")
    
    @cache_manager.cached(ttl=300, key_prefix="active_rules")
    def get_active_rules_by_product(
        self, 
        product_type: str, 
        effective_date: Optional[date] = None
    ) -> List[UnderwritingRule]:
        """Get active rules for product type"""
        try:
            effective_date = effective_date or date.today()
            
            query = self.db.query(UnderwritingRule).filter(
                UnderwritingRule.product_type == product_type,
                UnderwritingRule.is_active == True,
                UnderwritingRule.effective_from <= effective_date,
                or_(
                    UnderwritingRule.effective_to.is_(None),
                    UnderwritingRule.effective_to >= effective_date
                ),
                UnderwritingRule.archived_at.is_(None)
            ).order_by(desc(UnderwritingRule.priority), UnderwritingRule.order_index)
            
            return query.all()
            
        except Exception as e:
            raise DatabaseError(f"Failed to get active rules: {str(e)}")
    
    def search_rules(
        self, 
        filters: UnderwritingRuleSearchFilters,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = 'priority',
        sort_order: str = 'desc'
    ) -> Tuple[List[UnderwritingRule], int]:
        """Search rules with advanced filtering"""
        try:
            query = self.db.query(UnderwritingRule).filter(
                UnderwritingRule.archived_at.is_(None)
            )
            
            # Apply filters
            if filters.product_type:
                query = query.filter(UnderwritingRule.product_type == filters.product_type)
            
            if filters.rule_category:
                query = query.filter(UnderwritingRule.rule_category == filters.rule_category)
            
            if filters.rule_type:
                query = query.filter(UnderwritingRule.rule_type == filters.rule_type)
            
            if filters.is_active is not None:
                query = query.filter(UnderwritingRule.is_active == filters.is_active)
            
            if filters.decision_outcome:
                query = query.filter(UnderwritingRule.decision_outcome == filters.decision_outcome)
            
            if filters.priority_min is not None:
                query = query.filter(UnderwritingRule.priority >= filters.priority_min)
            
            if filters.priority_max is not None:
                query = query.filter(UnderwritingRule.priority <= filters.priority_max)
            
            if filters.effective_date:
                query = query.filter(
                    UnderwritingRule.effective_from <= filters.effective_date,
                    or_(
                        UnderwritingRule.effective_to.is_(None),
                        UnderwritingRule.effective_to >= filters.effective_date
                    )
                )
            
            if filters.search_text:
                search_term = f"%{filters.search_text}%"
                query = query.filter(
                    or_(
                        UnderwritingRule.rule_name.ilike(search_term),
                        UnderwritingRule.name.ilike(search_term),
                        UnderwritingRule.description.ilike(search_term)
                    )
                )
            
            # Get total count
            total_count = query.count()
            
            # Apply sorting
            sort_column = getattr(UnderwritingRule, sort_by, UnderwritingRule.priority)
            if sort_order.lower() == 'desc':
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
            
            # Apply pagination
            offset = (page - 1) * page_size
            rules = query.offset(offset).limit(page_size).all()
            
            return rules, total_count
            
        except Exception as e:
            raise DatabaseError(f"Failed to search rules: {str(e)}")
    
    def update_rule(self, rule_id: UUID, rule_data: dict, updated_by: UUID) -> UnderwritingRule:
        """Update underwriting rule"""
        try:
            rule = self.get_rule_by_id(rule_id)
            if not rule:
                raise EntityNotFoundError(f"Rule not found: {rule_id}")
            
            # Update fields
            for key, value in rule_data.items():
                if hasattr(rule, key) and key not in ['id', 'created_at', 'created_by']:
                    setattr(rule, key, value)
            
            rule.updated_by = updated_by
            rule.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(rule)
            
            # Clear cache
            self._clear_rules_cache()
            
            self.logger.info(f"Updated underwriting rule: {rule.rule_name} (ID: {rule.id})")
            return rule
            
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to update rule: {str(e)}")
    
    def delete_rule(self, rule_id: UUID, deleted_by: UUID) -> bool:
        """Soft delete underwriting rule"""
        try:
            rule = self.get_rule_by_id(rule_id)
            if not rule:
                raise EntityNotFoundError(f"Rule not found: {rule_id}")
            
            # Check if rule is being used
            if self._is_rule_in_use(rule_id):
                raise BusinessLogicError("Cannot delete rule that is currently in use")
            
            # Soft delete
            rule.archived_at = datetime.now()
            rule.updated_by = deleted_by
            rule.is_active = False
            
            self.db.commit()
            
            # Clear cache
            self._clear_rules_cache()
            
            self.logger.info(f"Deleted underwriting rule: {rule.rule_name} (ID: {rule.id})")
            return True
            
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to delete rule: {str(e)}")
    
    def bulk_create_rules(
        self, 
        rules_data: List[dict], 
        created_by: UUID,
        skip_duplicates: bool = True
    ) -> Tuple[List[UnderwritingRule], List[str]]:
        """Bulk create underwriting rules"""
        created_rules = []
        errors = []
        
        try:
            with self.db.begin():
                for rule_data in rules_data:
                    try:
                        # Check for duplicates if required
                        if skip_duplicates:
                            existing = self.get_rule_by_name(
                                rule_data.get('rule_name', ''),
                                rule_data.get('product_type', '')
                            )
                            if existing:
                                continue
                        
                        rule = UnderwritingRule(**rule_data)
                        rule.created_by = created_by
                        
                        self.db.add(rule)
                        self.db.flush()  # Get ID without committing
                        
                        created_rules.append(rule)
                        
                    except Exception as e:
                        errors.append(f"Failed to create rule '{rule_data.get('rule_name', 'Unknown')}': {str(e)}")
                        continue
            
            # Clear cache
            self._clear_rules_cache()
            
            self.logger.info(f"Bulk created {len(created_rules)} rules with {len(errors)} errors")
            return created_rules, errors
            
        except Exception as e:
            raise DatabaseError(f"Failed to bulk create rules: {str(e)}")
    
    def _is_rule_in_use(self, rule_id: UUID) -> bool:
        """Check if rule is currently in use"""
        try:
            # Check if rule has recent decisions (last 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            recent_decisions = self.db.query(UnderwritingDecision).filter(
                UnderwritingDecision.rule_id == rule_id,
                UnderwritingDecision.created_at >= thirty_days_ago
            ).first()
            
            return recent_decisions is not None
            
        except Exception:
            return True  # Err on the side of caution
    
    def _clear_rules_cache(self):
        """Clear rules-related cache entries"""
        cache_manager.clear_pattern("active_rules*")
    
    # =========================================================================
    # UNDERWRITING PROFILES REPOSITORY
    # =========================================================================
    
    def create_profile(self, profile_data: dict, created_by: Optional[UUID] = None) -> UnderwritingProfile:
        """Create new underwriting profile"""
        try:
            profile = UnderwritingProfile(**profile_data)
            if created_by:
                profile.created_by = created_by
            
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
            
            self.logger.info(f"Created underwriting profile: {profile.id}")
            return profile
            
        except IntegrityError as e:
            self.db.rollback()
            raise DatabaseError(f"Database integrity error: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to create profile: {str(e)}")
    
    def get_profile_by_id(self, profile_id: UUID, include_relationships: bool = False) -> Optional[UnderwritingProfile]:
        """Get underwriting profile by ID"""
        try:
            query = self.db.query(UnderwritingProfile).filter(
                UnderwritingProfile.id == profile_id,
                UnderwritingProfile.archived_at.is_(None)
            )
            
            if include_relationships:
                query = query.options(
                    selectinload(UnderwritingProfile.actions),
                    selectinload(UnderwritingProfile.documents),
                    selectinload(UnderwritingProfile.logs),
                    selectinload(UnderwritingProfile.decisions)
                )
            
            return query.first()
            
        except Exception as e:
            raise DatabaseError(f"Failed to get profile: {str(e)}")
    
    def get_profile_by_application(self, application_id: UUID) -> Optional[UnderwritingProfile]:
        """Get profile by application ID"""
        try:
            return self.db.query(UnderwritingProfile).filter(
                UnderwritingProfile.application_id == application_id,
                UnderwritingProfile.archived_at.is_(None)
            ).first()
            
        except Exception as e:
            raise DatabaseError(f"Failed to get profile by application: {str(e)}")
    
    def get_profile_by_member(self, member_id: UUID) -> List[UnderwritingProfile]:
        """Get profiles by member ID"""
        try:
            return self.db.query(UnderwritingProfile).filter(
                UnderwritingProfile.member_id == member_id,
                UnderwritingProfile.archived_at.is_(None)
            ).order_by(desc(UnderwritingProfile.created_at)).all()
            
        except Exception as e:
            raise DatabaseError(f"Failed to get profiles by member: {str(e)}")
    
    def search_profiles(
        self,
        filters: UnderwritingProfileSearchFilters,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = 'created_at',
        sort_order: str = 'desc'
    ) -> Tuple[List[UnderwritingProfile], int]:
        """Search profiles with advanced filtering"""
        try:
            query = self.db.query(UnderwritingProfile).filter(
                UnderwritingProfile.archived_at.is_(None)
            )
            
            # Apply filters
            if filters.member_id:
                query = query.filter(UnderwritingProfile.member_id == filters.member_id)
            
            if filters.status:
                query = query.filter(UnderwritingProfile.status == filters.status)
            
            if filters.decision:
                query = query.filter(UnderwritingProfile.decision == filters.decision)
            
            if filters.risk_level:
                query = query.filter(UnderwritingProfile.risk_level == filters.risk_level)
            
            if filters.assigned_to:
                query = query.filter(UnderwritingProfile.assigned_to == filters.assigned_to)
            
            if filters.priority_min is not None:
                query = query.filter(UnderwritingProfile.priority >= filters.priority_min)
            
            if filters.priority_max is not None:
                query = query.filter(UnderwritingProfile.priority <= filters.priority_max)
            
            if filters.is_overdue is not None:
                now = datetime.now()
                if filters.is_overdue:
                    query = query.filter(
                        UnderwritingProfile.sla_due_date < now,
                        UnderwritingProfile.status.not_in(['completed', 'cancelled'])
                    )
                else:
                    query = query.filter(
                        or_(
                            UnderwritingProfile.sla_due_date.is_(None),
                            UnderwritingProfile.sla_due_date >= now,
                            UnderwritingProfile.status.in_(['completed', 'cancelled'])
                        )
                    )
            
            if filters.evaluation_method:
                query = query.filter(UnderwritingProfile.evaluation_method == filters.evaluation_method)
            
            if filters.created_date_from:
                query = query.filter(UnderwritingProfile.created_at >= filters.created_date_from)
            
            if filters.created_date_to:
                query = query.filter(UnderwritingProfile.created_at <= filters.created_date_to)
            
            # Get total count
            total_count = query.count()
            
            # Apply sorting
            sort_column = getattr(UnderwritingProfile, sort_by, UnderwritingProfile.created_at)
            if sort_order.lower() == 'desc':
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
            
            # Apply pagination
            offset = (page - 1) * page_size
            profiles = query.offset(offset).limit(page_size).all()
            
            return profiles, total_count
            
        except Exception as e:
            raise DatabaseError(f"Failed to search profiles: {str(e)}")
    
    def update_profile(self, profile: UnderwritingProfile) -> UnderwritingProfile:
        """Update underwriting profile"""
        try:
            profile.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(profile)
            
            self.logger.info(f"Updated underwriting profile: {profile.id}")
            return profile
            
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to update profile: {str(e)}")
    
    def get_overdue_profiles(self, hours_overdue: int = 0) -> List[UnderwritingProfile]:
        """Get overdue profiles"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours_overdue)
            
            return self.db.query(UnderwritingProfile).filter(
                UnderwritingProfile.sla_due_date < cutoff_time,
                UnderwritingProfile.status.not_in(['completed', 'cancelled']),
                UnderwritingProfile.archived_at.is_(None)
            ).order_by(UnderwritingProfile.sla_due_date).all()
            
        except Exception as e:
            raise DatabaseError(f"Failed to get overdue profiles: {str(e)}")
    
    def get_high_priority_profiles(self) -> List[UnderwritingProfile]:
        """Get high priority profiles requiring attention"""
        try:
            return self.db.query(UnderwritingProfile).filter(
                UnderwritingProfile.priority <= 3,
                UnderwritingProfile.status.in_(['submitted', 'in_progress', 'review']),
                UnderwritingProfile.archived_at.is_(None)
            ).order_by(UnderwritingProfile.priority, UnderwritingProfile.created_at).all()
            
        except Exception as e:
            raise DatabaseError(f"Failed to get high priority profiles: {str(e)}")
    
    # =========================================================================
    # UNDERWRITING APPLICATIONS REPOSITORY
    # =========================================================================
    
    def create_application(self, application_data: dict, created_by: Optional[UUID] = None) -> UnderwritingApplication:
        """Create new underwriting application"""
        try:
            # Generate application number if not provided
            if 'application_number' not in application_data:
                application_data['application_number'] = self._generate_application_number(
                    application_data.get('product_type', 'GEN')
                )
            
            application = UnderwritingApplication(**application_data)
            if created_by:
                application.created_by = created_by
            
            # Set SLA due date if not provided
            if not application.sla_due_date:
                application.set_sla_due_date()
            
            self.db.add(application)
            self.db.commit()
            self.db.refresh(application)
            
            self.logger.info(f"Created underwriting application: {application.application_number} (ID: {application.id})")
            return application
            
        except IntegrityError as e:
            self.db.rollback()
            if "duplicate key" in str(e).lower():
                raise BusinessLogicError(f"Application number '{application_data.get('application_number')}' already exists")
            raise DatabaseError(f"Database integrity error: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to create application: {str(e)}")
    
    def get_application_by_id(self, application_id: UUID, include_relationships: bool = False) -> Optional[UnderwritingApplication]:
        """Get underwriting application by ID"""
        try:
            query = self.db.query(UnderwritingApplication).filter(
                UnderwritingApplication.id == application_id,
                UnderwritingApplication.archived_at.is_(None)
            )
            
            if include_relationships:
                query = query.options(
                    selectinload(UnderwritingApplication.decisions),
                    selectinload(UnderwritingApplication.documents),
                    selectinload(UnderwritingApplication.logs),
                    selectinload(UnderwritingApplication.communications),
                    selectinload(UnderwritingApplication.follow_ups)
                )
            
            return query.first()
            
        except Exception as e:
            raise DatabaseError(f"Failed to get application: {str(e)}")
    
    def get_application_by_number(self, application_number: str) -> Optional[UnderwritingApplication]:
        """Get application by application number"""
        try:
            return self.db.query(UnderwritingApplication).filter(
                UnderwritingApplication.application_number == application_number,
                UnderwritingApplication.archived_at.is_(None)
            ).first()
            
        except Exception as e:
            raise DatabaseError(f"Failed to get application by number: {str(e)}")
    
    def get_applications_by_member(self, member_id: UUID) -> List[UnderwritingApplication]:
        """Get applications by member ID"""
        try:
            return self.db.query(UnderwritingApplication).filter(
                UnderwritingApplication.member_id == member_id,
                UnderwritingApplication.archived_at.is_(None)
            ).order_by(desc(UnderwritingApplication.submitted_at)).all()
            
        except Exception as e:
            raise DatabaseError(f"Failed to get applications by member: {str(e)}")
    
    def search_applications(
        self,
        filters: UnderwritingApplicationSearchFilters,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = 'submitted_at',
        sort_order: str = 'desc'
    ) -> Tuple[List[UnderwritingApplication], int]:
        """Search applications with advanced filtering"""
        try:
            query = self.db.query(UnderwritingApplication).filter(
                UnderwritingApplication.archived_at.is_(None)
            )
            
            # Apply filters
            if filters.application_number:
                query = query.filter(UnderwritingApplication.application_number.ilike(f"%{filters.application_number}%"))
            
            if filters.member_id:
                query = query.filter(UnderwritingApplication.member_id == filters.member_id)
            
            if filters.product_type:
                query = query.filter(UnderwritingApplication.product_type == filters.product_type)
            
            if filters.status:
                query = query.filter(UnderwritingApplication.status == filters.status)
            
            if filters.priority:
                query = query.filter(UnderwritingApplication.priority == filters.priority)
            
            if filters.submission_channel:
                query = query.filter(UnderwritingApplication.submission_channel == filters.submission_channel)
            
            if filters.source:
                query = query.filter(UnderwritingApplication.source == filters.source)
            
            if filters.assigned_to:
                query = query.filter(UnderwritingApplication.assigned_to == filters.assigned_to)
            
            if filters.is_overdue is not None:
                now = datetime.now()
                if filters.is_overdue:
                    query = query.filter(
                        UnderwritingApplication.sla_due_date < now,
                        UnderwritingApplication.status.not_in(['approved', 'rejected', 'cancelled'])
                    )
                else:
                    query = query.filter(
                        or_(
                            UnderwritingApplication.sla_due_date.is_(None),
                            UnderwritingApplication.sla_due_date >= now,
                            UnderwritingApplication.status.in_(['approved', 'rejected', 'cancelled'])
                        )
                    )
            
            if filters.submitted_date_from:
                query = query.filter(UnderwritingApplication.submitted_at >= filters.submitted_date_from)
            
            if filters.submitted_date_to:
                query = query.filter(UnderwritingApplication.submitted_at <= filters.submitted_date_to)
            
            if filters.coverage_amount_min is not None:
                query = query.filter(UnderwritingApplication.coverage_amount >= filters.coverage_amount_min)
            
            if filters.coverage_amount_max is not None:
                query = query.filter(UnderwritingApplication.coverage_amount <= filters.coverage_amount_max)
            
            # Get total count
            total_count = query.count()
            
            # Apply sorting
            sort_column = getattr(UnderwritingApplication, sort_by, UnderwritingApplication.submitted_at)
            if sort_order.lower() == 'desc':
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
            
            # Apply pagination
            offset = (page - 1) * page_size
            applications = query.offset(offset).limit(page_size).all()
            
            return applications, total_count
            
        except Exception as e:
            raise DatabaseError(f"Failed to search applications: {str(e)}")
    
    def update_application(self, application: UnderwritingApplication) -> UnderwritingApplication:
        """Update underwriting application"""
        try:
            application.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(application)
            
            self.logger.info(f"Updated underwriting application: {application.application_number}")
            return application
            
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to update application: {str(e)}")
    
    def get_pending_applications(self, assigned_to: Optional[UUID] = None) -> List[UnderwritingApplication]:
        """Get pending applications for processing"""
        try:
            query = self.db.query(UnderwritingApplication).filter(
                UnderwritingApplication.status.in_(['submitted', 'in_progress', 'pending_info']),
                UnderwritingApplication.archived_at.is_(None)
            )
            
            if assigned_to:
                query = query.filter(UnderwritingApplication.assigned_to == assigned_to)
            
            return query.order_by(
                UnderwritingApplication.priority.desc(),
                UnderwritingApplication.submitted_at
            ).all()
            
        except Exception as e:
            raise DatabaseError(f"Failed to get pending applications: {str(e)}")
    
    def get_overdue_applications(self, hours_overdue: int = 0) -> List[UnderwritingApplication]:
        """Get overdue applications"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours_overdue)
            
            return self.db.query(UnderwritingApplication).filter(
                UnderwritingApplication.sla_due_date < cutoff_time,
                UnderwritingApplication.status.not_in(['approved', 'rejected', 'cancelled']),
                UnderwritingApplication.archived_at.is_(None)
            ).order_by(UnderwritingApplication.sla_due_date).all()
            
        except Exception as e:
            raise DatabaseError(f"Failed to get overdue applications: {str(e)}")
    
    def _generate_application_number(self, product_type: str) -> str:
        """Generate unique application number"""
        from datetime import datetime
        import random
        import string
        
        # Format: YYYYMMDD-PRODUCT-RANDOM
        date_part = datetime.now().strftime('%Y%m%d')
        product_part = product_type[:3].upper() if product_type else 'GEN'
        
        # Generate random part and ensure uniqueness
        max_attempts = 10
        for attempt in range(max_attempts):
            random_part = ''.join(random.choices(string.digits, k=6))
            application_number = f"{date_part}-{product_part}-{random_part}"
            
            # Check if number already exists
            existing = self.get_application_by_number(application_number)
            if not existing:
                return application_number
        
        # Fallback to timestamp-based number
        timestamp = int(datetime.now().timestamp())
        return f"{date_part}-{product_part}-{timestamp}"
    
    # =========================================================================
    # UNDERWRITING DECISIONS REPOSITORY
    # =========================================================================
    
    def create_decision(self, decision_data: dict) -> UnderwritingDecision:
        """Create underwriting decision record"""
        try:
            decision = UnderwritingDecision(**decision_data)
            
            self.db.add(decision)
            self.db.commit()
            self.db.refresh(decision)
            
            self.logger.info(f"Created underwriting decision: {decision.decision} for application {decision.application_id}")
            return decision
            
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to create decision: {str(e)}")
    
    def get_decisions_by_application(self, application_id: UUID) -> List[UnderwritingDecision]:
        """Get all decisions for an application"""
        try:
            return self.db.query(UnderwritingDecision).filter(
                UnderwritingDecision.application_id == application_id,
                UnderwritingDecision.archived_at.is_(None)
            ).order_by(desc(UnderwritingDecision.decision_date)).all()
            
        except Exception as e:
            raise DatabaseError(f"Failed to get decisions by application: {str(e)}")
    
    def get_decisions_by_profile(self, profile_id: UUID) -> List[UnderwritingDecision]:
        """Get all decisions for a profile"""
        try:
            return self.db.query(UnderwritingDecision).filter(
                UnderwritingDecision.profile_id == profile_id,
                UnderwritingDecision.archived_at.is_(None)
            ).order_by(desc(UnderwritingDecision.decision_date)).all()
            
        except Exception as e:
            raise DatabaseError(f"Failed to get decisions by profile: {str(e)}")
    
    def get_rule_evaluations_by_application(self, application_id: UUID) -> List[Dict[str, Any]]:
        """Get rule evaluations for application"""
        try:
            # This would typically involve a separate rule_evaluations table
            # For now, return decisions that include rule information
            decisions = self.get_decisions_by_application(application_id)
            
            evaluations = []
            for decision in decisions:
                if decision.rule_id:
                    evaluations.append({
                        'rule_id': decision.rule_id,
                        'decision': decision.decision,
                        'risk_score': decision.risk_score,
                        'premium_adjustment': decision.premium_adjustment,
                        'conditions_applied': decision.conditions_applied,
                        'decision_date': decision.decision_date,
                        'automated': decision.automated
                    })
            
            return evaluations
            
        except Exception as e:
            raise DatabaseError(f"Failed to get rule evaluations: {str(e)}")
    
    # =========================================================================
    # WORKFLOW REPOSITORY
    # =========================================================================
    
    def create_workflow(self, workflow_data: dict, created_by: UUID) -> UnderwritingWorkflow:
        """Create new workflow template"""
        try:
            workflow = UnderwritingWorkflow(**workflow_data)
            workflow.created_by = created_by
            
            self.db.add(workflow)
            self.db.commit()
            self.db.refresh(workflow)
            
            self.logger.info(f"Created workflow: {workflow.name} (ID: {workflow.id})")
            return workflow
            
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to create workflow: {str(e)}")
    
    def get_workflow_for_context(
        self, 
        product_type: str, 
        decision: Optional[str] = None,
        risk_level: Optional[Decimal] = None
    ) -> Optional[UnderwritingWorkflow]:
        """Get appropriate workflow for given context"""
        try:
            query = self.db.query(UnderwritingWorkflow).filter(
                UnderwritingWorkflow.is_active == True,
                UnderwritingWorkflow.archived_at.is_(None)
            )
            
            # Filter by product type
            query = query.filter(
                or_(
                    UnderwritingWorkflow.product_types.is_(None),
                    UnderwritingWorkflow.product_types.contains([product_type])
                )
            )
            
            # Order by specificity (more specific workflows first)
            workflows = query.order_by(
                desc(UnderwritingWorkflow.product_types.isnot(None)),
                desc(UnderwritingWorkflow.conditions.isnot(None)),
                UnderwritingWorkflow.created_at
            ).all()
            
            # Find the most appropriate workflow
            for workflow in workflows:
                if self._workflow_matches_context(workflow, product_type, decision, risk_level):
                    return workflow
            
            return None
            
        except Exception as e:
            raise DatabaseError(f"Failed to get workflow for context: {str(e)}")
    
    def get_default_workflow(self) -> Optional[UnderwritingWorkflow]:
        """Get default workflow"""
        try:
            return self.db.query(UnderwritingWorkflow).filter(
                UnderwritingWorkflow.is_default == True,
                UnderwritingWorkflow.is_active == True,
                UnderwritingWorkflow.archived_at.is_(None)
            ).first()
            
        except Exception as e:
            raise DatabaseError(f"Failed to get default workflow: {str(e)}")
    
    def create_workflow_execution(self, execution_data: dict) -> WorkflowExecution:
        """Create workflow execution instance"""
        try:
            execution = WorkflowExecution(**execution_data)
            
            self.db.add(execution)
            self.db.commit()
            self.db.refresh(execution)
            
            self.logger.info(f"Created workflow execution: {execution.id}")
            return execution
            
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to create workflow execution: {str(e)}")
    
    def get_active_workflow_execution(self, application_id: UUID) -> Optional[WorkflowExecution]:
        """Get active workflow execution for application"""
        try:
            return self.db.query(WorkflowExecution).filter(
                WorkflowExecution.application_id == application_id,
                WorkflowExecution.status.in_(['active', 'paused'])
            ).first()
            
        except Exception as e:
            raise DatabaseError(f"Failed to get active workflow execution: {str(e)}")
    
    def create_step_execution(self, step_execution_data: dict) -> WorkflowStepExecution:
        """Create workflow step execution"""
        try:
            step_execution = WorkflowStepExecution(**step_execution_data)
            
            self.db.add(step_execution)
            self.db.commit()
            self.db.refresh(step_execution)
            
            return step_execution
            
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to create step execution: {str(e)}")
    
    def update_step_execution(self, step_execution: WorkflowStepExecution) -> WorkflowStepExecution:
        """Update workflow step execution"""
        try:
            self.db.commit()
            self.db.refresh(step_execution)
            
            return step_execution
            
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to update step execution: {str(e)}")
    
    def _workflow_matches_context(
        self, 
        workflow: UnderwritingWorkflow, 
        product_type: str,
        decision: Optional[str] = None,
        risk_level: Optional[Decimal] = None
    ) -> bool:
        """Check if workflow matches the given context"""
        try:
            # Check product type
            if workflow.product_types and product_type not in workflow.product_types:
                return False
            
            # Check conditions if present
            if workflow.conditions:
                context = {
                    'product_type': product_type,
                    'decision': decision,
                    'risk_level': float(risk_level) if risk_level else None
                }
                
                # Simple condition evaluation (extend as needed)
                for condition_key, condition_value in workflow.conditions.items():
                    if condition_key in context:
                        if isinstance(condition_value, list):
                            if context[condition_key] not in condition_value:
                                return False
                        elif context[condition_key] != condition_value:
                            return False
            
            return True
            
        except Exception:
            return False
    
    # =========================================================================
    # ANALYTICS AND REPORTING
    # =========================================================================
    
    def get_underwriting_analytics(
        self, 
        start_date: date, 
        end_date: date,
        product_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get underwriting analytics for period"""
        try:
            query = self.db.query(UnderwritingApplication).filter(
                UnderwritingApplication.submitted_at >= start_date,
                UnderwritingApplication.submitted_at <= end_date,
                UnderwritingApplication.archived_at.is_(None)
            )
            
            if product_type:
                query = query.filter(UnderwritingApplication.product_type == product_type)
            
            applications = query.all()
            
            # Calculate statistics
            total_applications = len(applications)
            approved_applications = len([app for app in applications if app.status == 'approved'])
            rejected_applications = len([app for app in applications if app.status == 'rejected'])
            referred_applications = len([app for app in applications if app.status == 'referred'])
            
            approval_rate = (approved_applications / total_applications * 100) if total_applications > 0 else 0
            rejection_rate = (rejected_applications / total_applications * 100) if total_applications > 0 else 0
            referral_rate = (referred_applications / total_applications * 100) if total_applications > 0 else 0
            
            # Get risk distribution
            profiles = self.db.query(UnderwritingProfile).join(
                UnderwritingApplication,
                UnderwritingProfile.application_id == UnderwritingApplication.id
            ).filter(
                UnderwritingApplication.submitted_at >= start_date,
                UnderwritingApplication.submitted_at <= end_date,
                UnderwritingProfile.archived_at.is_(None)
            )
            
            if product_type:
                profiles = profiles.filter(UnderwritingApplication.product_type == product_type)
            
            profiles = profiles.all()
            
            risk_distribution = {}
            total_risk_score = 0
            valid_risk_scores = 0
            
            for profile in profiles:
                if profile.risk_level:
                    risk_distribution[profile.risk_level] = risk_distribution.get(profile.risk_level, 0) + 1
                
                if profile.risk_score:
                    total_risk_score += float(profile.risk_score)
                    valid_risk_scores += 1
            
            average_risk_score = total_risk_score / valid_risk_scores if valid_risk_scores > 0 else 0
            
            # Calculate processing times
            completed_applications = [app for app in applications if app.actual_completion_date and app.processing_started_at]
            processing_times = []
            
            for app in completed_applications:
                processing_time = (app.actual_completion_date - app.processing_started_at).total_seconds() / 3600
                processing_times.append(processing_time)
            
            average_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
            
            # Calculate SLA compliance
            sla_compliant = 0
            sla_total = 0
            
            for app in completed_applications:
                if app.sla_due_date:
                    sla_total += 1
                    if app.actual_completion_date <= app.sla_due_date:
                        sla_compliant += 1
            
            sla_compliance_rate = (sla_compliant / sla_total * 100) if sla_total > 0 else 0
            
            # Get distribution by product type and channel
            product_distribution = {}
            channel_distribution = {}
            
            for app in applications:
                product_distribution[app.product_type] = product_distribution.get(app.product_type, 0) + 1
                if app.submission_channel:
                    channel_distribution[app.submission_channel] = channel_distribution.get(app.submission_channel, 0) + 1
            
            return {
                'period_start': start_date,
                'period_end': end_date,
                'total_applications': total_applications,
                'approved_applications': approved_applications,
                'rejected_applications': rejected_applications,
                'referred_applications': referred_applications,
                'approval_rate': round(approval_rate, 2),
                'rejection_rate': round(rejection_rate, 2),
                'referral_rate': round(referral_rate, 2),
                'average_risk_score': round(average_risk_score, 2),
                'average_processing_time_hours': round(average_processing_time, 2),
                'sla_compliance_rate': round(sla_compliance_rate, 2),
                'risk_distribution': risk_distribution,
                'product_distribution': product_distribution,
                'channel_distribution': channel_distribution
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get underwriting analytics: {str(e)}")
    
    def get_performance_metrics(
        self, 
        start_date: date, 
        end_date: date,
        underwriter_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Get performance metrics for underwriter or system"""
        try:
            query = self.db.query(UnderwritingApplication).filter(
                UnderwritingApplication.submitted_at >= start_date,
                UnderwritingApplication.submitted_at <= end_date,
                UnderwritingApplication.archived_at.is_(None)
            )
            
            if underwriter_id:
                query = query.filter(
                    or_(
                        UnderwritingApplication.assigned_underwriter == underwriter_id,
                        UnderwritingApplication.decision_by == underwriter_id
                    )
                )
            
            applications = query.all()
            
            # Calculate metrics
            metrics = {
                'total_applications_processed': len(applications),
                'applications_approved': len([app for app in applications if app.status == 'approved']),
                'applications_rejected': len([app for app in applications if app.status == 'rejected']),
                'applications_referred': len([app for app in applications if app.status == 'referred']),
                'average_processing_time_hours': 0,
                'sla_compliance_rate': 0,
                'quality_score_average': 0,
                'productivity_score': 0
            }
            
            # Calculate processing times and SLA compliance
            completed_apps = [app for app in applications if app.actual_completion_date and app.processing_started_at]
            if completed_apps:
                processing_times = [
                    (app.actual_completion_date - app.processing_started_at).total_seconds() / 3600
                    for app in completed_apps
                ]
                metrics['average_processing_time_hours'] = round(sum(processing_times) / len(processing_times), 2)
                
                # SLA compliance
                sla_compliant = sum(1 for app in completed_apps if app.sla_due_date and app.actual_completion_date <= app.sla_due_date)
                sla_total = sum(1 for app in completed_apps if app.sla_due_date)
                metrics['sla_compliance_rate'] = round((sla_compliant / sla_total * 100), 2) if sla_total > 0 else 0
            
            # Calculate quality score
            quality_scores = [float(app.quality_score) for app in applications if app.quality_score]
            if quality_scores:
                metrics['quality_score_average'] = round(sum(quality_scores) / len(quality_scores), 2)
            
            # Calculate productivity (applications per day)
            days_in_period = (end_date - start_date).days + 1
            metrics['productivity_score'] = round(len(applications) / days_in_period, 2) if days_in_period > 0 else 0
            
            return metrics
            
        except Exception as e:
            raise DatabaseError(f"Failed to get performance metrics: {str(e)}")
    
    def get_risk_analysis(
        self, 
        start_date: date, 
        end_date: date,
        product_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get risk analysis for period"""
        try:
            query = self.db.query(UnderwritingProfile).join(
                UnderwritingApplication,
                UnderwritingProfile.application_id == UnderwritingApplication.id
            ).filter(
                UnderwritingApplication.submitted_at >= start_date,
                UnderwritingApplication.submitted_at <= end_date,
                UnderwritingProfile.archived_at.is_(None)
            )
            
            if product_type:
                query = query.filter(UnderwritingApplication.product_type == product_type)
            
            profiles = query.all()
            
            if not profiles:
                return {
                    'total_profiles': 0,
                    'average_risk_score': 0,
                    'risk_distribution': {},
                    'high_risk_profiles': 0,
                    'premium_adjustments': {'average_loading': 0, 'average_discount': 0}
                }
            
            # Calculate risk statistics
            risk_scores = [float(p.risk_score) for p in profiles if p.risk_score]
            premium_loadings = [float(p.premium_loading) for p in profiles if p.premium_loading]
            premium_discounts = [float(p.premium_discount) for p in profiles if p.premium_discount]
            
            risk_distribution = {}
            high_risk_count = 0
            
            for profile in profiles:
                if profile.risk_level:
                    risk_distribution[profile.risk_level] = risk_distribution.get(profile.risk_level, 0) + 1
                    
                    if profile.risk_level in ['high', 'very_high', 'unacceptable']:
                        high_risk_count += 1
            
            return {
                'total_profiles': len(profiles),
                'average_risk_score': round(sum(risk_scores) / len(risk_scores), 2) if risk_scores else 0,
                'risk_distribution': risk_distribution,
                'high_risk_profiles': high_risk_count,
                'high_risk_percentage': round((high_risk_count / len(profiles) * 100), 2) if profiles else 0,
                'premium_adjustments': {
                    'average_loading': round(sum(premium_loadings) / len(premium_loadings), 2) if premium_loadings else 0,
                    'average_discount': round(sum(premium_discounts) / len(premium_discounts), 2) if premium_discounts else 0,
                    'profiles_with_loading': len(premium_loadings),
                    'profiles_with_discount': len(premium_discounts)
                }
            }
            
        except Exception as e:
            raise DatabaseError(f"Failed to get risk analysis: {str(e)}")
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions"""
        try:
            yield self.db
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
    
    def execute_raw_query(self, query: str, params: Optional[Dict] = None) -> Any:
        """Execute raw SQL query"""
        try:
            return self.db.execute(text(query), params or {}).fetchall()
        except Exception as e:
            raise DatabaseError(f"Failed to execute raw query: {str(e)}")
    
    def get_table_statistics(self) -> Dict[str, int]:
        """Get basic table statistics"""
        try:
            stats = {}
            
            # Count records in main tables
            stats['underwriting_rules'] = self.db.query(UnderwritingRule).filter(
                UnderwritingRule.archived_at.is_(None)
            ).count()
            
            stats['underwriting_profiles'] = self.db.query(UnderwritingProfile).filter(
                UnderwritingProfile.archived_at.is_(None)
            ).count()
            
            stats['underwriting_applications'] = self.db.query(UnderwritingApplication).filter(
                UnderwritingApplication.archived_at.is_(None)
            ).count()
            
            stats['underwriting_decisions'] = self.db.query(UnderwritingDecision).filter(
                UnderwritingDecision.archived_at.is_(None)
            ).count()
            
            stats['workflow_executions'] = self.db.query(WorkflowExecution).count()
            
            return stats
            
        except Exception as e:
            raise DatabaseError(f"Failed to get table statistics: {str(e)}")
    
    def cleanup_old_records(self, days_old: int = 365) -> Dict[str, int]:
        """Clean up old archived records"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            cleanup_stats = {}
            
            # Clean up old archived rules
            old_rules = self.db.query(UnderwritingRule).filter(
                UnderwritingRule.archived_at < cutoff_date
            ).count()
            
            if old_rules > 0:
                self.db.query(UnderwritingRule).filter(
                    UnderwritingRule.archived_at < cutoff_date
                ).delete()
                cleanup_stats['rules_deleted'] = old_rules
            
            # Clean up old archived profiles
            old_profiles = self.db.query(UnderwritingProfile).filter(
                UnderwritingProfile.archived_at < cutoff_date
            ).count()
            
            if old_profiles > 0:
                self.db.query(UnderwritingProfile).filter(
                    UnderwritingProfile.archived_at < cutoff_date
                ).delete()
                cleanup_stats['profiles_deleted'] = old_profiles
            
            # Clean up old archived applications
            old_applications = self.db.query(UnderwritingApplication).filter(
                UnderwritingApplication.archived_at < cutoff_date
            ).count()
            
            if old_applications > 0:
                self.db.query(UnderwritingApplication).filter(
                    UnderwritingApplication.archived_at < cutoff_date
                ).delete()
                cleanup_stats['applications_deleted'] = old_applications
            
            self.db.commit()
            
            total_deleted = sum(cleanup_stats.values())
            self.logger.info(f"Cleaned up {total_deleted} old records")
            
            return cleanup_stats
            
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(f"Failed to cleanup old records: {str(e)}")
    
    def __del__(self):
        """Cleanup on destruction"""
        if hasattr(self, 'db') and self.db:
            try:
                self.db.close()
            except Exception:
                pass


# =============================================================================
# REPOSITORY FACTORY
# =============================================================================

class UnderwritingRepositoryFactory:
    """Factory for creating repository instances"""
    
    @staticmethod
    def create(db: Session) -> UnderwritingRepository:
        """Create repository instance"""
        return UnderwritingRepository(db)
    
    @staticmethod
    def create_with_caching(db: Session, cache_ttl: int = 300) -> UnderwritingRepository:
        """Create repository instance with custom cache TTL"""
        repository = UnderwritingRepository(db)
        repository.cache_ttl = cache_ttl
        return repository


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    'UnderwritingRepository',
    'UnderwritingRepositoryFactory'
]