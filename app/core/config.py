from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "21MAN API"
    app_env: str = "local"
    debug: bool = Field(default=True, validation_alias="APP_DEBUG")
    api_prefix: str = "/api/v1"
    backend_cors_origins: str = "http://localhost:3000,http://localhost:5173"
    database_url: str = "mysql+pymysql://worldbuild:worldbuild@localhost:3306/worldbuild"
    jwt_secret: str = Field(
        default="dev-change-this-jwt-secret-at-least-32-bytes",
        validation_alias=AliasChoices("JWT_SECRET", "JWT_SECRET_KEY"),
    )
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "worldbuild"
    jwt_audience: str = "worldbuild-api"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14
    bcrypt_rounds: int = 12
    ip_hash_secret: str = "dev-change-this-ip-secret-at-least-32-bytes"
    openai_api_key: str | None = None

    @property
    def access_token_expires_in(self) -> int:
        return self.access_token_expire_minutes * 60

    @property
    def refresh_token_expires_in(self) -> int:
        return self.refresh_token_expire_days * 24 * 60 * 60

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
