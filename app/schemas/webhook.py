from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class WebhookPayload(BaseModel):
    payment_id: UUID = Field(description="ID платежа")
    status: str = Field(description="Статус платежа (succeeded/failed)")
    amount: float | None = Field(None, description="Сумма платежа")
    currency: str | None = Field(None, description="Валюта")
    description: str | None = Field(None, description="Описание платежа")
    error_message: str | None = Field(None, description="Сообщение об ошибке")
    processed_at: datetime = Field(description="Время обработки")

    model_config = {
        "json_schema_extra": {
            "example": {
                "payment_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "succeeded",
                "amount": 1000.50,
                "currency": "RUB",
                "description": "Оплата заказа #12345",
                "error_message": None,
                "processed_at": "2024-01-01T12:05:00Z",
            }
        }
    }
