from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payments import Payment, PaymentStatus
from app.schemas.payments import PaymentCreate


class PaymentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_payment(
        self,
        *,
        payload: PaymentCreate,
        idempotency_key: str,
    ) -> Payment:
        payment = Payment(
            idempotency_key=idempotency_key,
            amount=payload.amount,
            currency=payload.currency,
            description=payload.description,
            metadata_json=payload.metadata,
            webhook_url=str(payload.webhook_url),
            status=PaymentStatus.PENDING,
        )
        self.session.add(payment)
        await self.session.flush()
        await self.session.refresh(payment)
        return payment

    async def get_by_id(self, payment_id: UUID) -> Payment | None:
        result = await self.session.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        return result.scalar_one_or_none()

    async def get_by_idempotency_key(self, idempotency_key: str) -> Payment | None:
        result = await self.session.execute(
            select(Payment).where(Payment.idempotency_key == idempotency_key)
        )
        return result.scalar_one_or_none()

    async def update_status(
        self,
        payment_id: UUID,
        *,
        status: PaymentStatus,
        processed_at: datetime | None = None,
    ) -> Payment | None:
        values: dict = {"status": status}
        if processed_at:
            values["processed_at"] = processed_at
        await self.session.execute(
            update(Payment).where(Payment.id == payment_id).values(**values)
        )
        await self.session.commit()
        return await self.get_by_id(payment_id)
