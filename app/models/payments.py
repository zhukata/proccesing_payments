from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    amount: Mapped[float]
    currency: Mapped[str] = mapped_column(length=3)
    description: Mapped[str] | None = None
    metadata: Mapped[dict] | None = None
    status: Mapped[str]
    indempotency_key: Mapped[str] = mapped_column(unique=True)
    webhook_url: Mapped[str] | None = None
    created_at: Mapped[str]
