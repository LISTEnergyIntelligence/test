from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    entsoe_token: str | None = Field(default=None, alias="ENTSOE_TOKEN")
    request_timeout_seconds: int = Field(default=30, alias="REQUEST_TIMEOUT_SECONDS")
    download_dir: Path = Field(default=Path("downloads"), alias="DOWNLOAD_DIR")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
settings.download_dir.mkdir(parents=True, exist_ok=True)
