import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy.sql import func
from sqlalchemy import DateTime


class ProductFeature(Base):
    __tablename__ = "product_features"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("product_catalog.id", ondelete="CASCADE"), nullable=False)
    name_en = Column(String(255), nullable=False)
    name_ar = Column(String(255))
    description = Column(Text)
    is_optional = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    product = relationship("ProductCatalog", back_populates="features")
