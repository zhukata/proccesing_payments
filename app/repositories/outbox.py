from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.outbox import Outbox


class OutboxRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_event(self, *, event_type: str, payload: dict) -> Outbox:
        event = Outbox(event_type=event_type, payload=payload)
        self.session.add(event)
        await self.session.flush()
        await self.session.refresh(event)
        return event

    async def get_unprocessed(self, limit: int = 20) -> list[Outbox]:
        result = await self.session.execute(
            select(Outbox)
            .where(Outbox.processed_at.is_(None))
            .order_by(Outbox.id)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def mark_processed(self, event: Outbox) -> None:
        event.processed_at = datetime.now(timezone.utc)
        self.session.add(event)
        await self.session.flush()
