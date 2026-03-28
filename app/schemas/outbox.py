from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class OutboxItem(BaseModel):
    id: int
    event_type: str = Field(description="Тип события")
    payload: dict = Field(description="Данные события")
    created_at: datetime
    processed_at: datetime | None = None

    model_config = {"from_attributes": True}


class OutboxPayload(BaseModel):
    payment_id: UUID = Field(description="ID платежа")
    webhook_url: str = Field(description="URL для вебхука")
    status: str = Field(description="Статус платежа (после обработки)")
    amount: float | None = Field(None, description="Сумма платежа")
    currency: str | None = Field(None, description="Валюта")
    description: str | None = Field(None, description="Описание платежа")
    error_message: str | None = Field(None, description="Сообщение об ошибке")

    model_config = {
        "json_schema_extra": {
            "example": {
                "payment_id": "123e4567-e89b-12d3-a456-426614174000",
                "webhook_url": "https://example.com/webhook",
                "status": "succeeded",
                "amount": 1000.50,
                "currency": "RUB",
                "description": "Оплата заказа #12345",
                "error_message": None,
            }
        }
    }
