from typing import Literal
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict



class CloudConfig(BaseSettings):
    provider: Literal[
        'cloudinary',
        's3',
        'r2',
    ] = 'cloudinary'

    # Cloudinary Setup
    cloudinary_api_key: str
    cloudinary_cloud_name: str
    cloudinary_api_secret: str

    # S3 Setup
    s3_api_key: str | None = None
    s3_api_secret: str | None = None
    s3_cloud_name: str | None = None

    # R2 Setup
    r2_api_key: str | None = None
    r2_api_secret: str | None = None
    r2_cloud_name: str | None = None

    model_config = SettingsConfigDict(
        env_prefix="CLOUD_",
        env_file_encoding='utf-8',
        env_file='.env',
        extra='ignore'
    )



@lru_cache
def get_cloud_settings() -> CloudConfig:
    return CloudConfig()