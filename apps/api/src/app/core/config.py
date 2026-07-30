from pydantic_settings import BaseSettings, SettingsConfigDict

from app.shared.ai.domain.entities.ai_provider_name import AIProviderName


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://postgres:postgres@localhost:54322/postgres"
    log_level: str = "INFO"
    api_key: str = "dev-local-api-key"
    ai_provider: AIProviderName = AIProviderName.MOCK


settings = Settings()
