from __future__ import annotations

from functools import lru_cache

import json

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore', enable_decoding=False)

    app_env: str = Field(default='development', alias='APP_ENV')
    app_name: str = Field(default='EDA-License-Monitor', alias='APP_NAME')
    api_v1_prefix: str = Field(default='/api/v1', alias='API_V1_PREFIX')
    database_url: str = Field(default='sqlite+aiosqlite:///./eda_license.db', alias='DATABASE_URL')
    sync_database_url: str | None = Field(default=None, alias='SYNC_DATABASE_URL')
    redis_url: str = Field(default='redis://localhost:6379/0', alias='REDIS_URL')
    celery_broker_url: str = Field(default='redis://localhost:6379/0', alias='CELERY_BROKER_URL')
    celery_result_backend: str = Field(default='redis://localhost:6379/1', alias='CELERY_RESULT_BACKEND')
    cors_origins_raw: str = Field(default='http://localhost:5173,http://localhost', alias='CORS_ORIGINS')
    collector_timeout_seconds: int = Field(default=20, alias='COLLECTOR_TIMEOUT_SECONDS')
    jwt_secret: str = Field(default='dev-secret-change-me', alias='JWT_SECRET')

    @field_validator('database_url', mode='before')
    @classmethod
    def normalize_database_url(cls, value):
        if isinstance(value, str) and value.startswith('postgresql://') and '+asyncpg' not in value:
            return value.replace('postgresql://', 'postgresql+asyncpg://', 1)
        return value

    @property
    def cors_origins(self) -> list[str]:
        raw = self.cors_origins_raw.strip()
        if not raw:
            return []
        if raw.startswith('['):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            except json.JSONDecodeError:
                pass
        return [item.strip().strip('"').strip("'") for item in raw.split(',') if item.strip()]

    @property
    def alembic_database_url(self) -> str:
        if self.sync_database_url:
            return self.sync_database_url
        if self.database_url.startswith('postgresql+asyncpg://'):
            return self.database_url.replace('postgresql+asyncpg://', 'postgresql+psycopg://', 1)
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
