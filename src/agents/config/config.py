from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os

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
    prompts_folder: Path

def read_config(config_path: Path) -> Config:
    load_dotenv(config_path)
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT")

    if not all([client_id, client_secret, user_agent]):
        raise ValueError(
            "Reddit API credentials not configured. Please set REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, and REDDIT_USER_AGENT")

    reddit_config = RedditConfig(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not configured. Please set OPENAI_API_KEY")

    llm = ChatOpenAI(
        model="gpt-4.1",
        temperature=0.1,
        api_key=api_key,
    )

    prompts_folder = os.getenv("PROMPTS_FOLDER")
    if not prompts_folder:
        raise ValueError("Prompts folder not configured. Please set PROMPTS_FOLDER")

    return Config(llm=llm, reddit_config=reddit_config, prompts_folder=Path(prompts_folder))
