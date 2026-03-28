from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")

    fast_model: str = "gpt-4o-mini"
    reasoning_model: str = "gpt-5"

    data_dir: str = "data"
    vector_db_path: str = "data/vector"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()