"""Configurazione centralizzata dell'applicazione."""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from datapizza.clients.google import GoogleClient


class Settings(BaseSettings):
    """Configurazione centralizzata dell'applicazione."""
    
    # Google/Gemini
    google_api_key: str
    gemini_model: str = "gemini-2.5-flash"
    
    # Rate Limiting
    gemini_rate_limit_rpm: int = 15
    gemini_rate_limit_rpd: int = 1500
    request_timeout_seconds: int = 30
    max_retries: int = 2
    
    # Tracing
    datapizza_agent_log_level: str = "DEBUG"
    enable_tracing: bool = False
    
    # Application
    app_env: str = "development"
    debug: bool = True
    log_level: str = "DEBUG"
    
    class Config:
        """Configurazione Pydantic."""
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Singleton per le settings."""
    return Settings()


def create_google_client(
    system_prompt: str,
    temperature: float = 0.7
) -> GoogleClient:
    """
    Factory function per creare istanze GoogleClient configurate.
    
    Args:
        system_prompt: Prompt di sistema per l'agente
        temperature: Creatività del modello (0.0-1.0)
    
    Returns:
        GoogleClient configurato per Gemini 2.5 Flash
    """
    settings = get_settings()
    
    return GoogleClient(
        api_key=settings.google_api_key,
        model=settings.gemini_model,
        system_prompt=system_prompt,
        temperature=temperature
    )