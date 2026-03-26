from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Outbox(Base):
    __tablename__ = "outbox"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    payload: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<Outbox {self.id} event_type={self.event_type} processed={self.processed_at is not None}>"