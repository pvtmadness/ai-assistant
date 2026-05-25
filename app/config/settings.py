from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
	default_fast_model: str = "gpt-4.1-mini"
	reasoning_model: str = "qwen3:14b"
	routing_model: str = "gpt-4.1-mini"
	openai_api_key: str
	
	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8",
		extra="ignore",
	)

settings = Settings()
