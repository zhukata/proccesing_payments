import asyncio
import contextlib
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers.payments import router as payments_router
from app.core.broker import (
    broker,
    dead_letter_exchange,
    dead_letter_queue,
    payments_exchange,
    payments_queue,
)
from app.services.outbox import outbox_dispatcher


@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.connect()
    await broker.declare_exchange(payments_exchange)
    await broker.declare_exchange(dead_letter_exchange)
    await broker.declare_queue(dead_letter_queue)
    await broker.declare_queue(payments_queue)
    dispatcher = asyncio.create_task(outbox_dispatcher())
    try:
        yield
    finally:
        dispatcher.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await dispatcher
        await broker.stop()


app = FastAPI(title="Processing Payments API", lifespan=lifespan)
app.include_router(payments_router)
