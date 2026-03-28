from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_KEY: str

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    RMQ_HOST: str
    RMQ_PORT: int
    RMQ_USER: str
    RMQ_PASSWORD: str

    PAYMENTS_EXCHANGE: str = "payments"
    PAYMENTS_QUEUE: str = "payments.new"
    DLX_NAME: str = "payments.dlx"
    DLQ_NAME: str = "payments.dead"

    @property
    def RMQ_DSN(self) -> str:
        return f"amqp://{self.RMQ_USER}:{self.RMQ_PASSWORD}@{self.RMQ_HOST}:{self.RMQ_PORT}/"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
