from sqlalchemy import Column, ForeignKey, Float, String
from app.core.database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

class ProviderServicePrice(Base):
    __tablename__ = "provider_service_prices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id"))
    service_name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, default="USD")
