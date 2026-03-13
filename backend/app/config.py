from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://eda_admin:password@localhost:5432/eda_license"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 2

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Collection
    COLLECTION_INTERVAL_SECONDS: int = 30
    LMSTAT_TIMEOUT_SECONDS: int = 10

    model_config = SettingsConfigDict(env_file=".env")

    @field_validator("JWT_SECRET")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """Warn if JWT_SECRET uses default value."""
        if v == "your-secret-key-change-in-production":
            raise ValueError(
                "JWT_SECRET must be changed from default value. "
                "Please set a secure secret key in production."
            )
        return v


settings = Settings()
