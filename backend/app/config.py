from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str
    jwt_secret: str
    bootstrap_tenant_slug: str = "demo"
    bootstrap_tenant_name: str = "Demo Tenant"
    bootstrap_admin_email: str
    bootstrap_admin_password: str
    bootstrap_ingestion_key: str
    demo_a_admin_email: str
    demo_a_admin_password: str
    demo_a_viewer_email: str
    demo_a_viewer_password: str
    demo_b_admin_email: str
    demo_b_admin_password: str
    demo_b_viewer_email: str
    demo_b_viewer_password: str
    access_token_expire_minutes: int = 60
    retention_days: int = 7
    retention_check_interval_seconds: int = 86400
    backend_cors_origins: str = "http://localhost:5173"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
