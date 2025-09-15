from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid


class ICD10Code(Base):
    __tablename__ = "icd10_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(20), unique=True, nullable=False)
    description_en = Column(String(255), nullable=False)
    description_ar = Column(String(255), nullable=True)
    chapter = Column(String(100), nullable=True)
