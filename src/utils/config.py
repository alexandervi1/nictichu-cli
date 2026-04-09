from pathlib import Path
from typing import Any, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    app_name: str = "NictichuCLI"
    app_version: str = "0.1.0"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    model_provider: Literal["ollama", "google_ai", "vertex_ai"] = "ollama"
    model_name: str = "gemma:7b"
    ollama_base_url: str = "http://localhost:11434"
    google_ai_api_key: str | None = None
    google_cloud_project: str | None = None
    google_cloud_location: str = "us-central1"
    brave_search_api_key: str | None = None


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def load_config(config_path: str | None = None) -> dict[str, Any]:
    """Cargar configuración desde archivo."""
    from pathlib import Path
    import yaml
    
    if config_path:
        path = Path(config_path)
        if path.exists():
            with open(path) as f:
                config_data = yaml.safe_load(f) or {}
                settings = get_settings()
                return {
                    "app_name": settings.app_name,
                    "app_version": settings.app_version,
                    "log_level": settings.log_level,
                    "model_provider": settings.model_provider,
                    "model_name": settings.model_name,
                    "ollama_base_url": settings.ollama_base_url,
                    "google_ai_api_key": settings.google_ai_api_key,
                    "google_cloud_project": settings.google_cloud_project,
                    "google_cloud_location": settings.google_cloud_location,
                    "brave_search_api_key": settings.brave_search_api_key,
                    **config_data
                }
        
    settings = get_settings()
    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "log_level": settings.log_level,
        "model_provider": settings.model_provider,
        "model_name": settings.model_name,
        "ollama_base_url": settings.ollama_base_url,
        "google_ai_api_key": settings.google_ai_api_key,
        "google_cloud_project": settings.google_cloud_project,
        "google_cloud_location": settings.google_cloud_location,
        "brave_search_api_key": settings.brave_search_api_key,
    }
