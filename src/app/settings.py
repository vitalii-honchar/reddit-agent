from pydantic_settings import BaseSettings


class BaseAppSettings(BaseSettings):
    """Base configuration for all modules"""
    db_url: str
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_prefix = "INDIE_HACKERS_AGENT_"
        extra = "allow"