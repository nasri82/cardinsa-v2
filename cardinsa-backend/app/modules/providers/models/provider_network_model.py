from sqlalchemy import Column, String, Text
from app.core.database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

class ProviderNetwork(Base):
    __tablename__ = "provider_networks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    tier = Column(String)  # Tier 1, Tier 2, VIP, Out-of-Network
    description = Column(Text)
