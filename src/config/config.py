from dataclasses import dataclass
from pathlib import Path

from langchain_core.language_models import BaseChatModel

@dataclass(frozen=True)
class RedditConfig:
    client_id: str
    client_secret: str
    user_agent: str

@dataclass(frozen=True)
class Config:
    llm: BaseChatModel
    reddit_config: RedditConfig
    prompt_folder: Path

