from faststream.rabbit import RabbitBroker, RabbitExchange, RabbitQueue

from app.core.config import settings

payments_exchange = RabbitExchange(
    settings.PAYMENTS_EXCHANGE,
    durable=True,
    type="direct",
)

payments_queue = RabbitQueue(
    settings.PAYMENTS_QUEUE,
    durable=True,
    routing_key=settings.PAYMENTS_QUEUE,
    exchange=payments_exchange,
    dead_letter_exchange=settings.DLX_NAME,
    dead_letter_routing_key=settings.DLQ_NAME,
)

dead_letter_exchange = RabbitExchange(settings.DLX_NAME, durable=True, type="direct")
dead_letter_queue = RabbitQueue(
    settings.DLQ_NAME,
    durable=True,
    routing_key=settings.DLQ_NAME,
    exchange=dead_letter_exchange,
)

broker = RabbitBroker(settings.RMQ_DSN)
