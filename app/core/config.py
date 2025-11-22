from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "OCR Pipeline API"
    fastapi_port: int = 8000

    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_topic: str = "demo-topic"
    kafka_group_id: str = "fastapi-consumer"

    redis_host: str = "redis"
    redis_port: int = 6379

    class Config:
        env_file = ".env"

settings = Settings()
