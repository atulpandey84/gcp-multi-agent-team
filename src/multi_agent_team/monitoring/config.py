from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"extra": "ignore"}
    api_key: str | None = None
    db_url: str = "sqlite:///./data/monitor.db"
    host: str = "0.0.0.0"
    port: int = 8000
    allowed_origins: list[str] = ["*"]
    max_agents: int = 22
    model_timeout: int = 120
    jwt_secret: str | None = None

    @classmethod
    def validate_settings(cls, s: "Settings") -> dict[str, bool]:
        """Validate core runtime settings."""
        return {
            "valid_port": 1 <= s.port <= 65535,
            "valid_agents": s.max_agents > 0,
            "valid_timeout": s.model_timeout > 0,
            "has_api_key": bool(s.api_key)
        }

settings = Settings()
