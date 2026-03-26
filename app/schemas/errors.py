from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    detail: str = Field(description="Описание ошибки")
    status_code: int = Field(description="HTTP статус код")

    model_config = {
        "json_schema_extra": {
            "example": {"detail": "Payment not found", "status_code": 404}
        }
    }
