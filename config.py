from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    x_admin_token: str 
    database_url: str
    secret_key: str
    user_password: str

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache()
def get_settings():
    return Settings()