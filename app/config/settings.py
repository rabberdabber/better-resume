from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Better Resume API"
    DEBUG: bool = True
    PORT: int = 8002
    HOST: str = "0.0.0.0"

    # Gemini API Configuration
    GEMINI_API_KEY: str

    # Google OAuth Configuration
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    # Test User Configuration
    TEST_USER_EMAIL: str

    # Google API Scopes
    GOOGLE_SCOPES: list = [
        "https://www.googleapis.com/auth/documents",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    # CORS
    CORS_ORIGINS: list = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


class TemplateSettings(BaseSettings):
    TEMPLATE_ID: str
    KOREAN_TEMPLATE_ID: str

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


@lru_cache()
def get_template_settings() -> TemplateSettings:
    return TemplateSettings()
