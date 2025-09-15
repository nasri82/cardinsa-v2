from sqlalchemy import Column, String, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Provider(Base):
    __tablename__ = "providers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    provider_type_id = Column(UUID(as_uuid=True), ForeignKey("provider_types.id"))
    city = Column(String)
    address = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    phone = Column(String)
    email = Column(String)
    website = Column(String)

    provider_type = relationship("ProviderType")
