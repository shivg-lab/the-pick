from pathlib import Path
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(BACKEND.parent / ".env",), extra="ignore")
    app_name: str = "The Pick"
    app_mode: Literal["demo", "hybrid", "fallback"] = "demo"
    llm_provider: Literal["ollama", "template"] = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "qwen3:8b"
    ollama_embedding_model: str = "embeddinggemma"
    llm_temperature: float = 0
    llm_timeout_seconds: float = 90
    provider_timeout_seconds: float = 12
    agent_max_steps: int = Field(default=4, ge=1, le=8)
    agent_max_tool_calls: int = Field(default=10, ge=6, le=20)
    event_provider: Literal["demo", "ticketmaster"] = "demo"
    sports_provider: Literal["demo", "sportradar"] = "demo"
    weather_provider: Literal["open_meteo", "disabled"] = "open_meteo"
    ticketmaster_api_key: str = ""
    sportradar_api_key: str = ""
    sportradar_feed_path: str = ""
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    data_dir: Path = BACKEND / "data"


settings = Settings()
