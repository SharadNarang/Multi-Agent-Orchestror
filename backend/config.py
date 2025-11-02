from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str = "sqlite:///./agent_orchestrator.db"
    redis_url: str = "redis://localhost:6379"
    groq_api_key: str = ""
    a2a_server_url: str = "http://localhost:8001"
    backend_api_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
