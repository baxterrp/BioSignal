from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "postgresql+asyncpg://biosignal:biosignal@localhost:5432/biosignal"
    ncbi_api_key: str = ""
    log_level: str = "INFO"


# Singleton — import this everywhere
settings = Settings()
