"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.

    All settings can be overridden via environment variables.
    """

    model_config = SettingsConfigDict(env_prefix="MASKER_")

    # API settings
    api_title: str = "Masker API"
    api_description: str = "PII Redaction & Text Anonymization API for LLMs and JSON"
    api_version: str = "1.0.0"

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000

    # Request limits
    max_text_size: int = 32 * 1024  # 32KB for text field
    max_payload_size: int = 64 * 1024  # 64KB for entire JSON payload
    request_timeout: int = 10  # 10s default timeout for intensive operations

    # Supported languages for NER
    supported_languages: list[str] = ["en", "ru"]
    default_language: str = "en"

    # Masking/redaction tokens (configurable defaults)
    mask_token: str = "***"
    redact_token: str = "[REDACTED]"

    # Placeholder templates for typed redaction
    placeholder_person: str = "<PERSON>"
    placeholder_email: str = "<EMAIL>"
    placeholder_phone: str = "<PHONE>"
    placeholder_card: str = "<CARD>"


# Global settings instance
settings = Settings()
