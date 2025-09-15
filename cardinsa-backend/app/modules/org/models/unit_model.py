from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Text, ForeignKey
from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin

class Unit(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "units"

    department_id: Mapped[str] = mapped_column(
        ForeignKey("departments.id", ondelete="CASCADE"),
        index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    code: Mapped[str | None] = mapped_column(String(60))
    description: Mapped[str | None] = mapped_column(Text())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    department = relationship("Department", back_populates="units", lazy="joined")
