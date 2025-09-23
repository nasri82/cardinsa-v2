# app/core/events.py

"""
Simple Events Module - Basic Implementation

Provides a basic event publishing system for the application.
This is a minimal implementation to prevent import errors.
Can be enhanced later with proper event handling infrastructure.
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from dataclasses import dataclass
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """Simple event data structure"""
    event_type: str
    data: Dict[str, Any]
    event_id: str = None
    timestamp: datetime = None
    source: str = None
    
    def __post_init__(self):
        if self.event_id is None:
            self.event_id = str(uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class SimpleEventPublisher:
    """
    Simple event publisher for basic event handling.
    This is a minimal implementation to get the service working.
    """
    
    def __init__(self):
        self.handlers: Dict[str, List[Callable]] = {}
        self.enabled = True
    
    def publish(self, event_type: str, data: Dict[str, Any], source: str = None) -> None:
        """
        Publish an event.
        
        Args:
            event_type: Type of event (e.g., "profile.created")
            data: Event data
            source: Source of the event
        """
        if not self.enabled:
            return
        
        try:
            event = Event(
                event_type=event_type,
                data=data,
                source=source
            )
            
            # Log the event
            logger.info(f"Event published: {event_type} from {source}")
            logger.debug(f"Event data: {data}")
            
            # Call registered handlers (if any)
            if event_type in self.handlers:
                for handler in self.handlers[event_type]:
                    try:
                        handler(event)
                    except Exception as e:
                        logger.error(f"Error in event handler for {event_type}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error publishing event {event_type}: {str(e)}")
    
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe a handler to an event type."""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Unsubscribe a handler from an event type."""
        if event_type in self.handlers:
            try:
                self.handlers[event_type].remove(handler)
            except ValueError:
                pass
    
    def disable(self) -> None:
        """Disable event publishing."""
        self.enabled = False
    
    def enable(self) -> None:
        """Enable event publishing."""
        self.enabled = True


# Global event publisher instance
_event_publisher = None


def get_event_publisher() -> SimpleEventPublisher:
    """Get the global event publisher instance."""
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = SimpleEventPublisher()
    return _event_publisher


# Create the event_publisher that the service is trying to import
event_publisher = get_event_publisher()


# Convenience functions for common events
def publish_profile_created(profile_id: UUID, profile_data: Dict[str, Any], created_by: UUID = None) -> None:
    """Publish profile created event."""
    event_publisher.publish(
        event_type="profile.created",
        data={
            "profile_id": str(profile_id),
            "profile_data": profile_data,
            "created_by": str(created_by) if created_by else None
        },
        source="pricing_profile_service"
    )


def publish_profile_updated(profile_id: UUID, changes: Dict[str, Any], updated_by: UUID = None) -> None:
    """Publish profile updated event."""
    event_publisher.publish(
        event_type="profile.updated",
        data={
            "profile_id": str(profile_id),
            "changes": changes,
            "updated_by": str(updated_by) if updated_by else None
        },
        source="pricing_profile_service"
    )


def publish_profile_deleted(profile_id: UUID, deleted_by: UUID = None) -> None:
    """Publish profile deleted event."""
    event_publisher.publish(
        event_type="profile.deleted",
        data={
            "profile_id": str(profile_id),
            "deleted_by": str(deleted_by) if deleted_by else None
        },
        source="pricing_profile_service"
    )


def publish_rule_added(profile_id: UUID, rule_id: UUID, added_by: UUID = None) -> None:
    """Publish rule added to profile event."""
    event_publisher.publish(
        event_type="profile.rule_added",
        data={
            "profile_id": str(profile_id),
            "rule_id": str(rule_id),
            "added_by": str(added_by) if added_by else None
        },
        source="pricing_profile_service"
    )


def publish_rule_removed(profile_id: UUID, rule_id: UUID, removed_by: UUID = None) -> None:
    """Publish rule removed from profile event."""
    event_publisher.publish(
        event_type="profile.rule_removed",
        data={
            "profile_id": str(profile_id),
            "rule_id": str(rule_id),
            "removed_by": str(removed_by) if removed_by else None
        },
        source="pricing_profile_service"
    )


# Export the main interfaces
__all__ = [
    'Event',
    'SimpleEventPublisher',
    'get_event_publisher',
    'event_publisher',
    'publish_profile_created',
    'publish_profile_updated',
    'publish_profile_deleted',
    'publish_rule_added',
    'publish_rule_removed'
]