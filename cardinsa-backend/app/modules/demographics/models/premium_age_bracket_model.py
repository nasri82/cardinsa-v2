from sqlalchemy import Column, Float, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid

class PremiumAgeBracket(Base):
    __tablename__ = "premium_age_brackets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=False)
    age_bracket_id = Column(UUID(as_uuid=True), ForeignKey("age_brackets.id"), nullable=False)
    multiplier = Column(Float, nullable=False)
    valid_from = Column(Date, nullable=True)
    valid_to = Column(Date, nullable=True)
