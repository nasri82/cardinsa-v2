"""
Audit Trail API Routes
Query and analyze system audit logs

SECURITY: Uses SQLAlchemy ORM to prevent SQL injection
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List
import uuid as uuid_lib
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.dependencies import get_current_user, CurrentUser
from app.modules.admin.models import AuditLog

router = APIRouter(prefix="/audit-trail", tags=["Admin - Audit Trail"])


@router.get("/logs", summary="Get Audit Logs")
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    entity_type: Optional[str] = None,
    action: Optional[str] = None,
    user_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get audit logs with filtering options

    Filters:
    - entity_type: Type of entity (policy, claim, user, etc.)
    - action: Action performed (create, update, delete, etc.)
    - user_id: User who performed the action
    - start_date/end_date: Date range filter

    SECURITY: Uses ORM query builder to prevent SQL injection
    """
    try:
        # Build query using ORM (safe from SQL injection)
        query = db.query(AuditLog)

        # Apply filters
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)

        if action:
            query = query.filter(AuditLog.action == action)

        if user_id:
            try:
                user_uuid = uuid_lib.UUID(user_id)
                query = query.filter(AuditLog.performed_by == user_uuid)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user_id format"
                )

        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)

        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)

        # Get total count before pagination
        total = query.count()

        # Apply ordering and pagination
        logs = (
            query
            .order_by(desc(AuditLog.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

        return {
            "logs": [log.to_dict() for log in logs],
            "total": total,
            "skip": skip,
            "limit": limit
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve audit logs: {str(e)}"
        )


@router.get("/entity/{entity_type}/{entity_id}", summary="Get Entity Audit History")
async def get_entity_audit_history(
    entity_type: str,
    entity_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get complete audit history for a specific entity

    SECURITY: Uses ORM query builder to prevent SQL injection
    """
    try:
        # Validate UUID format
        try:
            entity_uuid = uuid_lib.UUID(entity_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid entity_id format"
            )

        # Query using ORM (safe from SQL injection)
        history = (
            db.query(AuditLog)
            .filter(
                AuditLog.entity_type == entity_type,
                AuditLog.entity_id == entity_uuid
            )
            .order_by(desc(AuditLog.created_at))
            .all()
        )

        return {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "history": [log.to_dict() for log in history],
            "total_changes": len(history)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve entity history: {str(e)}"
        )


@router.get("/user/{user_id}/activity", summary="Get User Activity")
async def get_user_activity(
    user_id: str,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get user activity for specified number of days

    SECURITY: Uses ORM query builder to prevent SQL injection
    """
    try:
        # Validate UUID format
        try:
            user_uuid = uuid_lib.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user_id format"
            )

        start_date = datetime.now() - timedelta(days=days)

        # Query using ORM (safe from SQL injection)
        activity_query = (
            db.query(
                AuditLog.entity_type,
                AuditLog.action,
                func.count(AuditLog.id).label('count'),
                func.max(AuditLog.created_at).label('last_action')
            )
            .filter(
                AuditLog.performed_by == user_uuid,
                AuditLog.created_at >= start_date
            )
            .group_by(AuditLog.entity_type, AuditLog.action)
            .order_by(desc('count'))
            .all()
        )

        activity = []
        for row in activity_query:
            activity.append({
                "entity_type": row.entity_type,
                "action": row.action,
                "count": row.count,
                "last_action": row.last_action.isoformat() if row.last_action else None
            })

        return {
            "user_id": user_id,
            "period_days": days,
            "activity": activity,
            "total_actions": sum(a["count"] for a in activity)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user activity: {str(e)}"
        )


@router.get("/stats", summary="Get Audit Statistics")
async def get_audit_statistics(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Get audit trail statistics

    SECURITY: Uses ORM query builder to prevent SQL injection
    """
    try:
        start_date = datetime.now() - timedelta(days=days)

        # Total actions (using ORM)
        total_actions = (
            db.query(func.count(AuditLog.id))
            .filter(AuditLog.created_at >= start_date)
            .scalar()
        )

        # Actions by type (using ORM)
        actions_by_type_query = (
            db.query(
                AuditLog.entity_type,
                func.count(AuditLog.id).label('count')
            )
            .filter(AuditLog.created_at >= start_date)
            .group_by(AuditLog.entity_type)
            .order_by(desc('count'))
            .limit(10)
            .all()
        )
        actions_by_type = [
            {"entity_type": row.entity_type, "count": row.count}
            for row in actions_by_type_query
        ]

        # Most active users (using ORM)
        most_active_users_query = (
            db.query(
                AuditLog.performed_by,
                func.count(AuditLog.id).label('count')
            )
            .filter(
                AuditLog.created_at >= start_date,
                AuditLog.performed_by.isnot(None)
            )
            .group_by(AuditLog.performed_by)
            .order_by(desc('count'))
            .limit(10)
            .all()
        )
        most_active_users = [
            {"user_id": str(row.performed_by), "actions": row.count}
            for row in most_active_users_query
        ]

        return {
            "period_days": days,
            "total_actions": total_actions or 0,
            "actions_by_entity_type": actions_by_type,
            "most_active_users": most_active_users
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )
