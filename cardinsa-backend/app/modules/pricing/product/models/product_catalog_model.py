import uuid
from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy.sql import func
from sqlalchemy import DateTime


class ProductCatalog(Base):
    __tablename__ = "product_catalog"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name_en = Column(String(255), nullable=False)
    name_ar = Column(String(255))
    description = Column(Text)
    product_type = Column(String(50), nullable=False)  # e.g., medical, motor, life, travel
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    features = relationship("ProductFeature", back_populates="product", cascade="all, delete-orphan")
