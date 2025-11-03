# app/modules/providers/models/provider_model.py

"""
Enhanced Provider Model - Simplified Version
============================================

World-class implementation without external dependencies that might not exist yet.
We'll add relationships later as we build other models.
"""

from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, Numeric, Integer,
    ForeignKey, Index, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import validates
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from decimal import Decimal
from typing import Optional
from datetime import datetime

from app.core.database import Base
from app.core.mixins import AuditMixin, SoftDeleteMixin


class Provider(Base, AuditMixin, SoftDeleteMixin):
    """
    Provider Model
    
    Represents healthcare providers, auto repair shops, and other service providers
    in the insurance network ecosystem.
    
    Features:
    - Complete profile information with contact details
    - Geolocation support for proximity searches
    - Rating and review system integration
    - Network membership management
    - Service pricing and specialties
    - Comprehensive audit trail
    - Performance optimized queries
    """
    
    __tablename__ = "providers"
    
    # Primary key
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        comment="Unique identifier for provider"
    )
    
    # Core identification
    name = Column(
        String(255), 
        nullable=False,
        index=True,
        comment="Provider business name"
    )
    
    provider_type_id = Column(
        UUID(as_uuid=True),
        ForeignKey("provider_types.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Reference to provider type (hospital, clinic, auto repair, etc.)"
    )
    
    # Contact information
    email = Column(
        String(255),
        index=True,
        comment="Primary contact email"
    )
    
    phone = Column(
        String(50),
        comment="Primary contact phone number"
    )
    
    # Address and location
    address = Column(
        Text,
        comment="Street address"
    )
    
    city_id = Column(
        UUID(as_uuid=True),
        ForeignKey("cities.id", ondelete="SET NULL"),
        index=True,
        comment="Reference to city"
    )
    
    # Geolocation fields for proximity searches
    latitude = Column(
        Numeric(10, 8),
        comment="Latitude coordinate for location"
    )
    
    longitude = Column(
        Numeric(11, 8),
        comment="Longitude coordinate for location"
    )
    
    # Business information
    rating = Column(
        Numeric(3, 2),
        comment="Average customer rating (0.00 to 5.00)"
    )
    
    logo_url = Column(
        Text,
        comment="URL to provider logo/image"
    )
    
    website = Column(
        String(500),
        comment="Provider website URL"
    )
    
    # Status and operational info
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Whether provider is currently active and accepting patients/clients"
    )
    
    # Statistics (denormalized for performance)
    total_reviews = Column(
        Integer,
        default=0,
        comment="Total number of reviews received"
    )
    
    average_response_time = Column(
        Integer,
        comment="Average response time in minutes"
    )
    
    # Audit fields inherited from AuditMixin:
    # - created_at: DateTime(timezone=True)
    # - updated_at: DateTime(timezone=True) 
    # - created_by: UUID
    # - updated_by: UUID
    
    # Soft delete field inherited from SoftDeleteMixin:
    # - archived_at: DateTime(timezone=True)
    
    # Database constraints and indexes
    __table_args__ = (
        # Check constraints for data integrity
        CheckConstraint(
            "rating IS NULL OR (rating >= 0 AND rating <= 5)",
            name='ck_providers_rating_range'
        ),
        CheckConstraint(
            "latitude IS NULL OR (latitude >= -90 AND latitude <= 90)",
            name='ck_providers_latitude_range'
        ),
        CheckConstraint(
            "longitude IS NULL OR (longitude >= -180 AND longitude <= 180)",
            name='ck_providers_longitude_range'
        ),
        CheckConstraint(
            "total_reviews >= 0",
            name='ck_providers_total_reviews_positive'
        ),
        CheckConstraint(
            "average_response_time IS NULL OR average_response_time > 0",
            name='ck_providers_response_time_positive'
        ),
        CheckConstraint(
            "length(name) >= 2",
            name='ck_providers_name_length'
        ),
        CheckConstraint(
            "email IS NULL OR email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'",
            name='ck_providers_email_format'
        ),
        
        # Performance indexes
        Index('ix_providers_name_search', 'name', postgresql_using='gin'),
        Index('ix_providers_active', 'is_active'),
        Index('ix_providers_type_active', 'provider_type_id', 'is_active'),
        Index('ix_providers_city_active', 'city_id', 'is_active'),
        Index('ix_providers_rating', 'rating'),
        Index('ix_providers_email', 'email'),
        
        # Geospatial indexes for proximity searches
        Index(
            'ix_providers_location',
            'latitude', 'longitude',
            postgresql_where="latitude IS NOT NULL AND longitude IS NOT NULL"
        ),
        
        # Composite indexes for common queries
        Index(
            'ix_providers_type_city_active',
            'provider_type_id', 'city_id', 'is_active'
        ),
        Index(
            'ix_providers_rating_active',
            'rating', 'is_active',
            postgresql_where="rating IS NOT NULL"
        ),
        Index(
            'ix_providers_location_active',
            'latitude', 'longitude', 'is_active',
            postgresql_where="latitude IS NOT NULL AND longitude IS NOT NULL AND is_active = true"
        ),
        
        # Full-text search support
        Index(
            'ix_providers_fulltext',
            func.to_tsvector('english', 
                func.coalesce('name', '') + ' ' + 
                func.coalesce('address', '') + ' ' +
                func.coalesce('email', '')
            ),
            postgresql_using='gin'
        ),
        
        # Unique constraint for business logic
        UniqueConstraint(
            'name', 'city_id',
            name='uq_providers_name_city',
            deferrable=True  # Allow temporary violations during updates
        ),
        
        # Table comment
        {'comment': 'Healthcare providers, auto repair shops, and other service providers'}
    )
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<Provider(id={self.id}, name='{self.name}')>"
    
    def __str__(self) -> str:
        """Human-readable string representation"""
        return f"{self.name}"
    
    # Validation methods
    @validates('email')
    def validate_email(self, key, email):
        """Validate email format"""
        if email and '@' not in email:
            raise ValueError("Invalid email format")
        return email
    
    @validates('rating')
    def validate_rating(self, key, rating):
        """Validate rating is within acceptable range"""
        if rating is not None:
            rating = Decimal(str(rating))
            if not (0 <= rating <= 5):
                raise ValueError("Rating must be between 0 and 5")
        return rating
    
    @validates('phone')
    def validate_phone(self, key, phone):
        """Basic phone number validation"""
        if phone and len(phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')) < 10:
            raise ValueError("Phone number too short")
        return phone
    
    # Business methods
    def has_location(self) -> bool:
        """Check if provider has geolocation coordinates"""
        return self.latitude is not None and self.longitude is not None
    
    def is_highly_rated(self, threshold: Decimal = Decimal('4.0')) -> bool:
        """Check if provider has high rating"""
        return self.rating is not None and self.rating >= threshold
    
    def calculate_distance_km(self, target_lat: Decimal, target_lng: Decimal) -> Optional[float]:
        """Calculate distance to target coordinates in kilometers"""
        if not self.has_location():
            return None
            
        from math import radians, cos, sin, asin, sqrt
        
        # Convert to float for calculations
        lat1 = float(self.latitude)
        lng1 = float(self.longitude)
        lat2 = float(target_lat)
        lng2 = float(target_lng)
        
        # Haversine formula
        lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
        dlng = lng2 - lng1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers
        return c * r
    
    def update_rating(self, new_rating: Decimal, review_count_delta: int = 1):
        """Update provider rating with new review"""
        if self.rating is None:
            self.rating = new_rating
            self.total_reviews = review_count_delta
        else:
            # Calculate new average rating
            total_score = self.rating * self.total_reviews + new_rating
            self.total_reviews += review_count_delta
            self.rating = total_score / self.total_reviews if self.total_reviews > 0 else Decimal('0')
    
    def deactivate(self, reason: str = None, updated_by: UUID = None):
        """Deactivate provider with optional reason"""
        self.is_active = False
        if updated_by:
            self.updated_by = updated_by
    
    def activate(self, updated_by: UUID = None):
        """Activate provider"""
        self.is_active = True
        if updated_by:
            self.updated_by = updated_by
    
    # Serialization helpers
    def to_dict(self, include_location: bool = True) -> dict:
        """Convert to dictionary for API responses"""
        result = {
            'id': str(self.id),
            'name': self.name,
            'provider_type_id': str(self.provider_type_id),
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city_id': str(self.city_id) if self.city_id else None,
            'rating': float(self.rating) if self.rating else None,
            'logo_url': self.logo_url,
            'website': self.website,
            'is_active': self.is_active,
            'total_reviews': self.total_reviews,
            'average_response_time': self.average_response_time,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_location:
            result.update({
                'latitude': float(self.latitude) if self.latitude else None,
                'longitude': float(self.longitude) if self.longitude else None,
                'has_location': self.has_location()
            })
        
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Provider':
        """Create instance from dictionary"""
        return cls(
            name=data['name'],
            provider_type_id=data['provider_type_id'],
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
            city_id=data.get('city_id'),
            latitude=Decimal(str(data['latitude'])) if data.get('latitude') else None,
            longitude=Decimal(str(data['longitude'])) if data.get('longitude') else None,
            logo_url=data.get('logo_url'),
            website=data.get('website'),
            is_active=data.get('is_active', True)
        )


# Export the model
__all__ = ['Provider']