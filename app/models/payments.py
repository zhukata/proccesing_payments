from datetime import datetime
from decimal import Decimal
from enum import Enum as PyEnum
from uuid import uuid4

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PaymentStatus(str, PyEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"

    def __str__(self) -> str:
        return self.value


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=func.gen_random_uuid(),
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    metadata: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        default=None,
    )
    webhook_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status"),
        nullable=False,
        default=PaymentStatus.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<Payment {self.id} status={self.status}>"
