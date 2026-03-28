from fastapi import Header, status, HTTPException
from app.core.config import settings


async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> str:
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key"
        )
    return x_api_key


async def get_idempotency_key(
    x_idempotency_key: str = Header(..., alias="Idempotency-Key"),
    min_length: int = 1,
    max_length: int = 255,
) -> str:
    if not (min_length <= len(x_idempotency_key) <= max_length):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Idempotency-Key must be between {min_length} and {max_length} characters",
        )
    return x_idempotency_key
