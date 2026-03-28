from faststream.rabbit import ExchangeType, RabbitBroker, RabbitExchange, RabbitQueue

from app.core.config import settings

payments_exchange = RabbitExchange(
    settings.PAYMENTS_EXCHANGE,
    durable=True,
    type=ExchangeType.DIRECT,
)

payments_queue = RabbitQueue(
    settings.PAYMENTS_QUEUE,
    durable=True,
    routing_key=settings.PAYMENTS_QUEUE,
    arguments={
        "x-dead-letter-exchange": settings.DLX_NAME,
        "x-dead-letter-routing-key": settings.DLQ_NAME,
    },
)

dead_letter_exchange = RabbitExchange(
    settings.DLX_NAME, durable=True, type=ExchangeType.DIRECT
)
dead_letter_queue = RabbitQueue(
    settings.DLQ_NAME,
    durable=True,
    routing_key=settings.DLQ_NAME,
)

broker = RabbitBroker(settings.RMQ_DSN)
