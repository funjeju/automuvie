from functools import lru_cache
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    env: str = "development"
    api_base_url: str = "http://localhost:8000"
    cors_origins: str = "http://localhost:3000"

    firebase_project_id: str = ""
    firebase_private_key: str = ""
    firebase_client_email: str = ""
    firebase_storage_bucket: str = ""
    google_application_credentials: str = ""

    # CLAUDE_API_KEY / ANTHROPIC_API_KEY 둘 다 받음
    claude_api_key: str = Field(
        default="", validation_alias=AliasChoices("CLAUDE_API_KEY", "ANTHROPIC_API_KEY")
    )
    openai_api_key: str = ""
    # Google Gemini/Imagen/Veo (Google AI Studio) — GOOGLE_GENERATIVE_AI_API_KEY로도 받음
    google_genai_api_key: str = Field(
        default="", validation_alias=AliasChoices("GOOGLE_GENAI_API_KEY", "GOOGLE_GENERATIVE_AI_API_KEY")
    )
    youtube_api_key: str = ""
    lyria_api_key: str = ""
    veo_api_key: str = ""
    whisper_api_key: str = ""

    jwt_secret: str = "change_me"
    temp_dir: str = "./temp"
    output_dir: str = "./output"

    lyrics_provider: str = "mock"
    music_provider: str = "mock"
    image_provider: str = "mock"
    video_provider: str = "mock"
    subtitle_provider: str = "mock"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
