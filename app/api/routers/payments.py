from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_idempotency_key, verify_api_key
from app.core.database import get_db
from app.models.payments import PaymentStatus
from app.repositories.outbox import OutboxRepository
from app.repositories.payments import PaymentRepository
from app.schemas.outbox import OutboxPayload
from app.schemas.payments import PaymentCreate, PaymentResponse

router = APIRouter(
    prefix="/api/v1", tags=["payments"], dependencies=[Depends(verify_api_key)]
)


@router.post(
    "/payments", status_code=status.HTTP_202_ACCEPTED, response_model=PaymentResponse
)
async def create_payment(
    payment: PaymentCreate,
    session: AsyncSession = Depends(get_db),
    idempotency_key: str = Depends(get_idempotency_key),
):
    repo = PaymentRepository(session)
    async with session.begin():
        existing = await repo.get_by_idempotency_key(idempotency_key)
        if existing:
            logger.info(
                "Idempotent hit: payment reused idempotency_key={}", idempotency_key
            )
            return PaymentResponse.model_validate(existing)

        created = await repo.create_payment(
            payload=payment,
            idempotency_key=idempotency_key,
        )
        logger.info("Payment created id={} ikey={}", created.id, idempotency_key)

        outbox_repo = OutboxRepository(session)
        await outbox_repo.add_event(
            event_type="payment.created",
            payload=OutboxPayload(
                payment_id=created.id,
                webhook_url=created.webhook_url,
                status=PaymentStatus.PENDING.value,
                amount=float(created.amount),
                currency=created.currency,
                description=created.description,
                error_message=None,
            ).model_dump(mode="json"),
        )
        logger.info("Outbox event enqueued for payment id={}", created.id)

    return PaymentResponse.model_validate(created)


@router.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: str, db: AsyncSession = Depends(get_db)):
    try:
        pid = UUID(payment_id)
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid payment_id format"
        ) from None

    repo = PaymentRepository(db)
    payment = await repo.get_by_id(pid)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return PaymentResponse.model_validate(payment)
