from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LangCall"
    use_mock_llm: bool = False
    litellm_model: str = "dashscope/qwen3-max-2026-01-23"
    dashscope_api_key: str | None = None
    raw_calls_dir: str = "data/raw_calls"
    output_dir: str = "data/outputs"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "langcall"
    postgres_user: str = "langcall"
    postgres_password: str = "langcall123"

    redis_host: str = "localhost"
    redis_port: int = 6379
    
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_from: str = "langcall@example.com"
    report_to: str = "manager@example.com"
    report_timezone: str = "Asia/Shanghai"
    report_hour: int = 8
    report_minute: int = 0
    worker_poll_interval_seconds: int = 3
    webhook_idempotency_ttl_seconds: int = 30
    call_processing_lock_ttl_seconds: int = 120
    max_retry_count: int = 3
    retry_backoff_base_seconds: int = 2

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parents[2]

    @property
    def raw_calls_path(self) -> Path:
        return self.project_root / self.raw_calls_dir

    @property
    def output_path(self) -> Path:
        return self.project_root / self.output_dir

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/0"


settings = Settings()
