from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    text_analysis_model: str = "anthropic/claude-3.5-sonnet"
    image_prompt_model: str = "anthropic/claude-3.5-sonnet"
    image_generation_model: str = "openai/dall-e-3"
    default_scenes_count: int = 10
    
    volcengine_access_key: str = ""
    volcengine_secret_key: str = ""
    volcengine_region: str = "cn-north-1"
    volcengine_tts_model: str = "tts-1"

    class Config:
        env_file = ".env"


settings = Settings()
