from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, field_validator


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class PaymentCreate(BaseModel):
    amount: Decimal = Field(
        description="Сумма платежа", gt=0, decimal_places=2, examples=[1000.50]
    )
    currency: str = Field(
        description="Валюта платежа",
        pattern="^(RUB|USD|EUR)$",
        examples=["RUB"],
    )
    description: str | None = Field(
        None, max_length=500, description="Описание платежа"
    )
    metadata: dict | None = Field(
        None,
        description="Дополнительные метаданные",
        examples=[{"order_id": "12345", "custumer_id": "45321"}],
    )
    webhook_url: HttpUrl = Field(
        description="URL для уведомления о результате платежа",
        examples=["https://example.com/webhook"],
    )

    @field_validator
    @classmethod
    def validate_currency(cls, value: str) -> str:
        allowed = {"RUB", "USD", "EUR"}
        if value not in allowed:
            raise ValueError(f"Currency ,ust be one of {allowed}")
        return value


class PaymentResponse(BaseModel):
    id: UUID = Field(description="Уникальный идентификатор платежа")
    amount: Decimal = Field(description="Сумма платежа")
    currency: str = Field(description="Валюта платежа")
    description: str | None = Field(None, description="Описание платежа")
    metadata: dict | None = Field(None, description="Метаданные платежа")
    webhook_url: HttpUrl = Field(description="URL для вебхука")
    status: PaymentStatus = Field(description="Статус платежа")
    created_at: datetime = Field(description="Дата создания")
    processed_at: datetime | None = Field(None, description="Дата обработки")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "amount": 1000.50,
                "currency": "RUB",
                "description": "Оплата заказа #12345",
                "metadata": {"order_id": "12345"},
                "webhook_url": "https://example.com/webhook",
                "status": "pending",
                "created_at": "2024-01-01T12:00:00Z",
                "processed_at": None,
            }
        },
    }


class PaymentUpdate(BaseModel):
    status: PaymentStatus
    processed_at: datetime | None = None
