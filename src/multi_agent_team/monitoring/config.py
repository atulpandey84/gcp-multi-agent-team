from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"extra": "ignore"}
    api_key: str | None = None
    db_url: str = "sqlite:///./data/monitor.db"
    host: str = "0.0.0.0"
    port: int = 8000
    allowed_origins: list[str] = ["*"]

    # Environment variables should be prefixed with MONITORING_.
    # Example: MONITORING_API_KEY


settings = Settings()
