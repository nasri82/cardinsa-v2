# app/modules/org/models/company_model.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Text
from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin

class Company(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    code: Mapped[str | None] = mapped_column(String(60), unique=True)
    description: Mapped[str | None] = mapped_column(Text())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    departments = relationship("Department", back_populates="company", lazy="selectin")
