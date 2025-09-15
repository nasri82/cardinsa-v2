from sqlalchemy import Column, ForeignKey
from app.core.database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

class ProviderNetworkMember(Base):
    __tablename__ = "provider_network_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id"))
    provider_network_id = Column(UUID(as_uuid=True), ForeignKey("provider_networks.id"))
