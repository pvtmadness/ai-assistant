from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
	default_fast_model: str = "gpt-4.1-mini"
	reasoning_model: str = "qwen3:14b"
	routing_model: str = "gpt-4.1-mini"
	openai_api_key: str
	device_role: str = "lenovo"
	execution_profile: str = "lenovo_primary"
	memory_write_policy: str = "enabled"

	@field_validator("device_role")
	@classmethod
	def validate_device_role(cls, value: str) -> str:
		allowed = {"lenovo", "laptop"}
		normalized = value.strip().lower()
		if normalized not in allowed:
			raise ValueError(f"device_role must be one of: {sorted(allowed)}")
		return normalized

	@field_validator("execution_profile")
	@classmethod
	def validate_execution_profile(cls, value: str) -> str:
		allowed = {"lenovo_primary", "laptop_light"}
		normalized = value.strip().lower()
		if normalized not in allowed:
			raise ValueError(f"execution_profile must be one of: {sorted(allowed)}")
		return normalized

	@field_validator("memory_write_policy")
	@classmethod
	def validate_memory_write_policy(cls, value: str) -> str:
		allowed = {"disabled", "build_only", "manual_review", "enabled"}
		normalized = value.strip().lower()
		if normalized not in allowed:
			raise ValueError(f"memory_write_policy must be one of: {sorted(allowed)}")
		return normalized
	
	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8",
		extra="ignore",
	)

settings = Settings()
