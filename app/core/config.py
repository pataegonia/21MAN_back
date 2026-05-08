from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "21MAN API"
    app_env: str = "local"
    debug: bool = Field(default=True, validation_alias="APP_DEBUG")
    api_prefix: str = "/api/v1"
    backend_cors_origins: str = "http://localhost:3000,http://localhost:5173"
    database_url: str = "mysql+pymysql://worldbuild:worldbuild@localhost:3306/worldbuild"
    jwt_secret_key: str = "change-this-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14
    ip_hash_secret: str = "change-this-ip-secret"
    openai_api_key: str | None = None

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
