# from typing import Literal
# from functools import lru_cache
# from pydantic import SecretStr
# from pydantic_settings import BaseSettings, SettingsConfigDict



# class Settings(BaseSettings):




#     # --------------------------------------------------
#     # Application Configuration
#     # --------------------------------------------------
#     app_name: str
#     app_version: str


#     environment: Literal[
#         'development',
#         'production',
#         'testing'
#     ]

#     debug: bool



#     log_level: str


#     # --------------------------------------------------
#     # CORS Configuration
#     # --------------------------------------------------
#     cors_origin: list[str]




#     # --------------------------------------------------
#     # JWT Configuration
#     # --------------------------------------------------
#     jwt_secret: SecretStr
#     jwt_algorithm: str
#     jwt_access_token_expires_minutes: int



#     model_config = SettingsConfigDict(
#         env_file=".env",
#         case_sensitive=False,
#         extra='ignore',
#         env_file_encoding='utf-8'
#     )



# @lru_cache
# def get_settings() -> Settings:
#     return Settings()





from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "Interview Platform API"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    API_V1_PREFIX: str = "/api/v1"

    # --- MongoDB ---
    MONGO_URI: str = Field(..., description="e.g. mongodb+srv://user:pass@cluster.mongodb.net")
    MONGODB_DB_NAME: str = "interview_db"

    # --- Redis (ARQ job queue) ---
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- Security / JWT ---
    JWT_SECRET_KEY: str = Field(..., min_length=32, description="32+ char random string")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- CORS ---
    CORS_ORIGINS: list[str] = ["https://nexora-prep.vercel.app","http://localhost:3000"]

    # --- Resume uploads ---
    UPLOAD_DIR: str = "uploads"
    MAX_RESUME_MB: int = 5

    # --- Abuse / cost control ---
    MAX_ACTIVE_SESSIONS: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @model_validator(mode="after")
    def _reject_placeholder_secret_in_prod(self) -> "Settings":
        if self.APP_ENV == "production" and self.JWT_SECRET_KEY.startswith("change-me"):
            raise ValueError("JWT_SECRET_KEY must be changed for production")
        return self

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def max_resume_bytes(self) -> int:
        return self.MAX_RESUME_MB * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """Parsed once per process; override in tests via cache_clear()."""
    return Settings()
