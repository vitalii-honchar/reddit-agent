import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from langchain_openai import ChatOpenAI

from agents.config import Config, RedditConfig
from agents.search_agent import CreateSearchAgentCommand, execute_search
from core.models import AgentExecution
from scheduler.settings import SchedulerSettings

logger = logging.getLogger("uvicorn")

@dataclass
class AgentExecutor:
    settings: SchedulerSettings

    async def execute(self, agent_execution: AgentExecution) -> dict[str, Any]:
        logger.info("Executing agent: execution_id = %s, agent_type = %s, executions = %s", agent_execution.id,
                    agent_execution.config.agent_type,
                    agent_execution.executions)

        match agent_execution.config.agent_type:
            case "search_agent":
                cfg = self._create_config()
                cmd = CreateSearchAgentCommand.model_validate(agent_execution.config.data)
                logger.info("Executing search agent: execution_id = %s, cmd = %s", agent_execution.id, cmd)
                res = await execute_search(cfg, cmd)
                return res.model_dump()
            case _:
                raise RuntimeError(f"Unknown agent_type {agent_execution.config.agent_type}")

    def _create_config(self) -> Config:
        return Config(
            llm=ChatOpenAI(
                model=self.settings.llm_model,
                temperature=self.settings.llm_model_temperature,
                api_key=self.settings.openai_api_key # type: ignore
            ),
            reddit_config=RedditConfig(
                client_id=self.settings.reddit_client_id,
                client_secret=self.settings.reddit_client_secret,
                user_agent=self.settings.reddit_agent,
            ),
            prompts_folder=Path(self.settings.prompts_folder)
        )
