from pika import ConnectionParameters, PlainCredentials
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    @property
    def DATABASE_URL(self) -> str:
        return f"asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    RMQ_HOST: str
    RMQ_PORT: int
    RMQ_USER: str
    RMQ_PASSWORD: str

    @property
    def CONNECTION_PARAMETERS(self) -> ConnectionParameters:
        return ConnectionParameters(
            host=self.RMQ_HOST,
            port=self.RMQ_PORT,
            credentials=PlainCredentials(self.RMQ_USER, self.RMQ_PASSWORD),
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
