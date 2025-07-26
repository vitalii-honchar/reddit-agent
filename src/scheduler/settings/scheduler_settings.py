from pydantic_settings import BaseSettings

class SchedulerSettings(BaseSettings):
    reddit_client_id: str
    reddit_client_secret: str
    reddit_agent: str
    openai_api_key: str
    llm_model: str = 'gpt-4.1'
    llm_model_temperature: float = 0.1
    prompts_folder: str = 'prompts'
    db_url: str
    debug: bool = False
    poll_interval_seconds: float = 1
    threshold_seconds: float = 600
    max_retries: int = 3


    class Config:
        env_file = ".env"
        env_prefix = "INDIE_HACKERS_AGENT"
