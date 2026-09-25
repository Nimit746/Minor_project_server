from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    
    # LLM Config
    groq_api_key: str | None = None
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None



    # Model Config
    groq_default_model: str = "allam-2-7b"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    anthropic_model: str | None = None
    openai_model: str | None = None



    # Huggingface API for fast loading of models
    hf_token: str | None = None


    # Qdrant config
    qdrant_url: str | None = "http://localhost:6333"
    qdrant_api_key: str | None = None



    chunk_size: int = 1000
    chunk_overlap: int = 200


    tavily_api_key: str


    mongo_uri: str = "mongodb://localhost:27017"
    mongo_pass: str | None = None
    mongo_db_name: str = "interview_prep"



    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_file_encoding='utf-8',
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()