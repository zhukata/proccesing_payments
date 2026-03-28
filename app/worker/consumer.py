import asyncio
import random
from datetime import datetime, timezone
from uuid import UUID

import httpx
from faststream import FastStream
from faststream.rabbit import RabbitMessage

from app.core.broker import broker, payments_queue
from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.models.payments import PaymentStatus
from app.repositories.payments import PaymentRepository

app = FastStream(broker)


async def send_webhook(url: str, payload: dict, attempts: int = 3) -> bool:
    delay = 1
    async with httpx.AsyncClient(timeout=5) as client:
        for attempt in range(attempts):
            try:
                response = await client.post(url, json=payload)
                if response.status_code < 400:
                    return True
            except Exception:
                # swallow and retry
                pass
            await asyncio.sleep(delay)
            delay *= 2
    return False


@broker.subscriber(payments_queue)
async def process_payment(message: dict, msg: RabbitMessage):
    payment_id = UUID(str(message["payment_id"]))
    attempt = int(msg.headers.get("x-retry", 0))

    try:
        async with AsyncSessionLocal() as session:
            repo = PaymentRepository(session)

            # simulate processing 2-5 seconds
            await asyncio.sleep(random.uniform(2, 5))
            succeeded = random.random() <= 0.9
            status = PaymentStatus.SUCCEEDED if succeeded else PaymentStatus.FAILED
            processed_at = datetime.now(timezone.utc)
            await repo.update_status(
                payment_id, status=status, processed_at=processed_at
            )
            updated = await repo.get_by_id(payment_id)

        webhook_payload = {
            "payment_id": str(payment_id),
            "status": status.value,
            "amount": (
                float(message.get("amount"))
                if message.get("amount") is not None
                else None
            ),
            "currency": message.get("currency"),
            "description": updated.description if updated else None,
            "error_message": None if succeeded else "Processing error",
            "processed_at": processed_at.isoformat(),
        }

        delivered = await send_webhook(message["webhook_url"], webhook_payload)
        if not delivered:
            raise RuntimeError("Webhook delivery failed after retries")

        await msg.ack()
    except Exception:
        if attempt >= 2:
            await msg.reject(requeue=False)
        else:
            await asyncio.sleep(2**attempt)
            # requeue with incremented retry counter
            await broker.publish(
                message, queue=settings.PAYMENTS_QUEUE, headers={"x-retry": attempt + 1}
            )
            await msg.ack()
