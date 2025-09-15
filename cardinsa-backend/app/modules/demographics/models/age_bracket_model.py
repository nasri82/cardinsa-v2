from sqlalchemy import Column, String, Integer, Enum, Date
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid
import enum

class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"

class InsuranceTypeEnum(str, enum.Enum):
    medical = "medical"
    motor = "motor"
    life = "life"
    travel = "travel"

class AgeBracket(Base):
    __tablename__ = "age_brackets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    min_age = Column(Integer, nullable=False)
    max_age = Column(Integer, nullable=False)
    gender = Column(Enum(GenderEnum), nullable=True)
    insurance_type = Column(Enum(InsuranceTypeEnum), nullable=True)
    effective_date = Column(Date, nullable=True)
