from pydantic import BaseModel, Field


class IdempotencyKey(BaseModel):
    key: str = Field(min_length=1, max_length=255)

    model_config = {"from_attributes": True}
