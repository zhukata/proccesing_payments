import asyncio

from loguru import logger

from app.core.broker import broker
from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.repositories.outbox import OutboxRepository


async def publish_event(payload: dict) -> None:
    await broker.publish(payload, queue=settings.PAYMENTS_QUEUE)


async def outbox_dispatcher(poll_interval: float = 1.0) -> None:
    """Continuously poll outbox table and publish new events to RabbitMQ."""
    while True:
        async with AsyncSessionLocal() as session:
            repo = OutboxRepository(session)
            async with session.begin():
                events = await repo.get_unprocessed()
                for event in events:
                    try:
                        await publish_event(event.payload)
                        logger.info("Outbox published event id={}", event.id)
                    except Exception as exc:  # noqa: BLE001
                        logger.warning(
                            "Outbox publish failed for id={} error={}",
                            event.id,
                            exc,
                        )
                        # leave unprocessed to retry in next loop
                        break
                    await repo.mark_processed(event)
        await asyncio.sleep(poll_interval)
