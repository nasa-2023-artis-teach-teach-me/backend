from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MAP_KEY: str
    DATABASE_URL: str
    S3_ENDPOINT_URL: str
    S3_BUCKET_NAME: str
    S3_ACCESS_KEY_ID: str
    S3_SECRET_ACCESS_KEY: str
    model_config = SettingsConfigDict(env_file=".env")