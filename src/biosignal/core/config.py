from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "postgresql+asyncpg://biosignal:biosignal@localhost:5432/biosignal"
    ncbi_api_key: str = ""
    log_level: str = "INFO"
    max_concurrent_requests: int = 5
    pubmed_base_url: str = "https://eutils.ncbi.nlm.nih.gov"


# Singleton — import this everywhere
settings = Settings()
