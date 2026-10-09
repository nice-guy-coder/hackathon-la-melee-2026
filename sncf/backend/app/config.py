from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

APP_VERSION = "0.1.0"
DEFAULT_DATA_DIR = Path(__file__).resolve().parent / "mock"


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def _csv(name: str, default: str) -> tuple[str, ...]:
    raw = os.getenv(name, default)
    return tuple(item.strip() for item in raw.split(",") if item.strip())


def _bool(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    environment: str = "development"
    app_version: str = APP_VERSION
    data_source: str = "mock"
    data_dir: Path = field(default_factory=lambda: DEFAULT_DATA_DIR)
    cors_origins: tuple[str, ...] = (
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    )
    allowed_hosts: tuple[str, ...] = ("localhost", "127.0.0.1", "[::1]")
    enable_docs: bool = True
    top_n: int = 5
    max_request_bytes: int = 65536
    llm_enabled: bool = False
    llm_base_url: str = "http://localhost:11434/v1"
    llm_api_key: str = field(default="", repr=False)
    llm_model: str = "qwen2.5-coder:14b"
    llm_timeout_seconds: float = 15.0

    @property
    def is_production(self) -> bool:
        return self.environment.casefold() == "production"

    def safe_summary(self) -> dict[str, object]:
        return {
            "environment": self.environment,
            "app_version": self.app_version,
            "data_source": self.data_source,
            "llm_enabled": self.llm_enabled,
            "docs_enabled": self.enable_docs,
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    _load_dotenv()
    environment = os.getenv("ENVIRONMENT", "development")
    docs_default = "false" if environment.casefold() == "production" else "true"
    return Settings(
        environment=environment,
        data_source=os.getenv("DATA_SOURCE", "mock"),
        data_dir=Path(os.getenv("DATA_DIR", str(DEFAULT_DATA_DIR))),
        cors_origins=_csv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"),
        allowed_hosts=_csv("ALLOWED_HOSTS", "localhost,127.0.0.1,[::1]"),
        enable_docs=_bool("ENABLE_DOCS", docs_default),
        top_n=int(os.getenv("TOP_N", "5")),
        max_request_bytes=int(os.getenv("MAX_REQUEST_BYTES", "65536")),
        llm_enabled=_bool("LLM_ENABLED", "false"),
        llm_base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1"),
        llm_api_key=os.getenv("LLM_API_KEY", ""),
        llm_model=os.getenv("LLM_MODEL", "qwen2.5-coder:14b"),
        llm_timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "15")),
    )
