from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(os.getenv("MKA_ROOT_DIR", Path(__file__).resolve().parents[2])).resolve()
load_dotenv(ROOT_DIR / ".env.local")


@dataclass(frozen=True, slots=True)
class Settings:
    root_dir: Path = ROOT_DIR
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5-mini")
    ai_provider: str = os.getenv("MKA_AI_PROVIDER", "auto").lower()
    cors_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv(
            "MKA_CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173"
        ).split(",")
        if origin.strip()
    )

    @property
    def data_dir(self) -> Path:
        return self.root_dir / "data"

    @property
    def evals_dir(self) -> Path:
        return self.root_dir / "evals"

    @property
    def openai_enabled(self) -> bool:
        return bool(self.openai_api_key) and self.ai_provider in {"auto", "openai"}


settings = Settings()
