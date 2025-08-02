from app.settings import BaseAppSettings
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel


class SchedulerConfig(BaseAppSettings):
    """Configuration for Scheduler module"""
    reddit_client_id: str
    reddit_client_secret: str
    reddit_agent: str
    openai_api_key: str
    openai_endpoint: str | None = None
    openai_site_url: str | None = None
    openai_site_name: str | None = None
    llm_model: str = 'gpt-4.1'
    llm_model_temperature: float = 0.1
    llm_model_max_tokens: int = 4000
    prompts_folder: str = 'prompts'
    poll_interval_seconds: float = 1
    threshold_seconds: float = 60
    max_retries: int = 20
    
    def create_llm(self) -> BaseChatModel:
        llm_kwargs = {
            "model": self.llm_model,
            "temperature": self.llm_model_temperature,
            "max_tokens": self.llm_model_max_tokens,
            "api_key": self.openai_api_key,
        }
        
        if self.openai_endpoint is not None:
            llm_kwargs["base_url"] = self.openai_endpoint
            
            # Add OpenRouter-required headers when using custom endpoint
            default_headers = {}
            if self.openai_site_url is not None:
                default_headers["HTTP-Referer"] = self.openai_site_url
            if self.openai_site_name is not None:
                default_headers["X-Title"] = self.openai_site_name
                
            if default_headers:
                llm_kwargs["default_headers"] = default_headers
            
        return ChatOpenAI(**llm_kwargs)