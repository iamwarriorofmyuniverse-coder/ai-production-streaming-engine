from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "Production AI Streaming Engine"
    API_V1_STR: str = "/api/v1"
    
    # API Keys
    GROQ_API_KEY: str = Field(default="", description="Groq API Key (Optional for fallback)")
    GEMINI_API_KEY: str = Field(default="", description="Gemini API Key (Optional)")
    
    # Redis Settings
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Async Redis URL")
    
    # Rate Limiting & Caching Controls
    RATE_LIMIT_PER_MINUTE: int = 30
    CACHE_TTL_SECONDS: int = 3600  # 1 Hour exact cache
    MAX_CONCURRENT_REQUESTS: int = 50

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
