from typing import Callable

import asyncpraw
from langchain_core.messages import HumanMessage, BaseMessage, ToolMessage, AIMessage
from langgraph.prebuilt import create_react_agent

from agents.config import Config
from agents.prompt import PromptManager
from agents.search_agent.models import CreateSearchAgentCommand, SearchResult
from agents.search_agent.tool import create_reddit_tools
import logging

logger = logging.getLogger("uvicorn")


async def execute_search(cfg: Config, cmd: CreateSearchAgentCommand) -> SearchResult:
    prompt_manager = PromptManager(cfg.prompts_folder)
    search_agent_prompt = prompt_manager.load_prompt("search_agent", "system")
    
    # Create tools and track Reddit clients for cleanup
    tools, reddit_clients = await _create_tools(cfg, cmd)
    
    try:
        agent = create_react_agent(
            model=cfg.llm,
            tools=tools,
            response_format=SearchResult,
            prompt=search_agent_prompt.format(behavior=cmd.behavior, min_results=cmd.min_results),
        ).with_config(recursion_limit=cmd.recursion_limit)

        messages = [HumanMessage(cmd.search_query)]

        res = None
        async for event in agent.astream({"messages": messages}, stream_mode='values'):
            _log_message(event["messages"][-1])
            res = event

        if res is None:
            raise RuntimeError("No search results found")
        return res["structured_response"]
    finally:
        # Clean up Reddit clients
        for reddit_client in reddit_clients:
            await reddit_client.close()


def _log_message(message: BaseMessage):
    params = {
        "type": message.type,
        "content": message.content,
        "content_length": str(len(message.content)),
    }

    if isinstance(message, ToolMessage):
        params["tool_name"] = message.name
        params["tool_call_id"] = message.tool_call_id
    elif isinstance(message, AIMessage):
        tool_calls = [{"name": t["name"], "id": t["id"]} for t in message.tool_calls]
        params["tool_calls"] = str(tool_calls)
        params["tool_calls_size"] = str(len(tool_calls))

    logger.info("Handle message: %s", params)




async def _create_tools(cfg: Config, cmd: CreateSearchAgentCommand) -> tuple[list[Callable], list[asyncpraw.Reddit]]:
    tools = []
    reddit_clients = []

    for search_type in cmd.search_types:
        if search_type == "reddit":
            reddit = asyncpraw.Reddit(
                client_id=cfg.reddit_config.client_id,
                client_secret=cfg.reddit_config.client_secret,
                user_agent=cfg.reddit_config.user_agent,
            )
            reddit_clients.append(reddit)
            tools.extend(create_reddit_tools(reddit))

    return tools, reddit_clients
