# Processing Payments

Асинхронный сервис для приёма платежей, публикации событий в RabbitMQ и обработки их воркером с эмуляцией внешнего платёжного шлюза и отправкой вебхуков.

## Стек
- FastAPI + Pydantic v2
- SQLAlchemy 2 (async, asyncpg) + Alembic
- RabbitMQ (FastStream)
- PostgreSQL
- Docker / docker-compose

## Запуск через Docker Compose
```bash
docker compose up --build
```
Сервис поднимет:
- API на http://localhost:8000
- Postgres на 5432
- RabbitMQ mgmt UI на http://localhost:15672 (guest/guest)

## Переменные окружения
См. `.env.example`. Основные:
- `API_KEY` — обязательный ключ для заголовка `X-API-Key`
- `DB_*` — настройки PostgreSQL
- `RMQ_*` — настройки RabbitMQ

## Миграции
В docker-командах уже выполняется `alembic upgrade head`.
Для локального запуска:
```bash
export $(cat .env.example | xargs)  # или свой .env
alembic upgrade head
```

## Локальный запуск без Docker
```bash
uvicorn app.main:app --reload
# отдельно воркер
faststream run app.worker.consumer:app
```
Требуется запущенные Postgres и RabbitMQ (можно из docker-compose).

## API
Все запросы требуют заголовок `X-API-Key` и (для POST) `Idempotency-Key`.

### Создать платёж
`POST /api/v1/payments`
```bash
curl -X POST http://localhost:8000/api/v1/payments \
  -H 'X-API-Key: supersecret' \
  -H 'Idempotency-Key: order-123' \
  -H 'Content-Type: application/json' \
  -d '{
    "amount": 1000.50,
    "currency": "RUB",
    "description": "Оплата заказа #123",
    "metadata": {"order_id": "123"},
    "webhook_url": "https://example.com/webhook"
  }'
```
Ответ: `202 Accepted` с данными платежа.

### Получить платёж
`GET /api/v1/payments/{payment_id}`
```bash
curl -H 'X-API-Key: supersecret' http://localhost:8000/api/v1/payments/<uuid>
```

## Поток обработки
1. API создаёт запись `payments` + событие в таблице `outbox` (идемпотентность по `Idempotency-Key`).
2. Фоновая задача outbox публикует событие в очередь `payments.new`.
3. Consumer (FastStream) читает из `payments.new`, эмулирует обработку (2–5 сек, 90% успех), обновляет статус платежа.
4. Consumer отправляет вебхук с результатом (3 попытки, экспоненциальная задержка). При повторных провалах — сообщение отклоняется без requeue и попадает в DLQ `payments.dead`.
5. Очередь настроена с DLQ и ручным подсчётом ретраев (3 попытки: публикация с заголовком `x-retry`).

## Структура
- `app/main.py` — FastAPI, запуск outbox-диспетчера
- `app/api/routers/payments.py` — эндпоинты
- `app/models/*` — ORM модели
- `app/repositories/*` — доступ к БД
- `app/services/outbox.py` — публикация событий
- `app/worker/consumer.py` — воркер/consumer
- `alembic/` — миграции

## Проверка
- Создайте платёж (POST), затем убедитесь в статусе через GET.
- В RabbitMQ UI мониторьте `payments.new` и `payments.dead`.
- Для отладки вебхуков можно использовать https://webhook.site/ (подставить URL в `webhook_url`).
