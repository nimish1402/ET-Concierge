"""
ET AI Concierge - Core Application Settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # LLM API Keys
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # Weaviate
    WEAVIATE_URL: str = "http://localhost:8080"
    WEAVIATE_API_KEY: str = ""

    # App
    APP_ENV: str = "development"
    FRONTEND_URL: str = "http://localhost:3000"


settings = Settings()
