from functools import lru_cache

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Hitech FPV API"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    database_url: str = "postgresql://postgres:postgres@localhost:5432/hitech_fpv"
    database_pool_min_size: int = Field(default=1, ge=1)
    database_pool_max_size: int = Field(default=10, ge=1)

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @field_validator("api_prefix")
    @classmethod
    def normalize_api_prefix(cls, value: str) -> str:
        value = "/" + value.strip("/")
        return value if value != "/" else ""

    @model_validator(mode="after")
    def validate_database_pool_bounds(self) -> "Settings":
        if self.database_pool_max_size < self.database_pool_min_size:
            raise ValueError(
                "DATABASE_POOL_MAX_SIZE must be greater than or equal to "
                "DATABASE_POOL_MIN_SIZE"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
