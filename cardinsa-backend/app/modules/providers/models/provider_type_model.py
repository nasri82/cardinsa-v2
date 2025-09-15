from sqlalchemy import Column, String
from app.core.database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

class ProviderType(Base):
    __tablename__ = "provider_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False, unique=True)
    category = Column(String, nullable=False)  # medical / motor / other
