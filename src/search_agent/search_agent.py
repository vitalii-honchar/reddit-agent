from typing import Callable

import praw
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

from config import Config
from search_agent.models import CreateSearchAgentCommand, SearchResult
from search_agent.tool import create_reddit_tools
import logging

logger = logging.getLogger(__name__)

SEARCH_AGENT_PROMPT = """You are a relentless search agent whose goal is to uncover at least {min_results} actionable insights on the topic specified in the behaviour and user input.  
Use every available tool in turn, reformulating queries as needed, until you either exhaust all reasonable angles or hit hard rate limits.

--- Search Strategy ---
1. Diversify phrasing: synonyms, jargon, casual vs. technical  
2. Zoom in and out: start broad → refine → broaden again  
3. Cross-platform: mix searches across Reddit, Google, StackOverflow, etc.  
4. Iterate on results: build new queries from your findings  
5. Validate: seek corroboration across at least two independent sources

--- Persistence Rules ---
- If a search returns sparse results, immediately rephrase & retry  
- If you’re rate-limited, switch to another tool  
- “No results” = rethink keywords, never stop  
- Continue until you have ≥{min_results} distinct, high-value findings or all tools are blocked

--- Reporting Requirements ---
- For each iteration, record:  
  • The exact query you issued  
  • The tool you used  
  • Why you chose that angle  
- At the end, state your confidence in search completeness

<BEHAVIOR>
{behavior}
</BEHAVIOR>
"""



def execute_search(cfg: Config, cmd: CreateSearchAgentCommand) -> SearchResult:
    agent = create_react_agent(
        model=cfg.llm,
        tools=_create_tools(cfg, cmd),
        response_format=SearchResult,
        prompt=SEARCH_AGENT_PROMPT.format(behavior=cmd.behavior, min_results=cmd.min_results),
    )

    messages = [HumanMessage(cmd.search_query)]
    input = {"messages": messages}

    for event in agent.stream(input, stream_mode='values'):
        logger.info("Event received: %s", event["messages"][-1])
        res = event

    return res["structured_response"]

def _create_tools(cfg: Config, cmd: CreateSearchAgentCommand) -> list[Callable]:
    tools = []

    for search_type in cmd.search_types:
        if search_type == "reddit":
            reddit = praw.Reddit(
                client_id=cfg.reddit_config.client_id,
                client_secret=cfg.reddit_config.client_secret,
                user_agent=cfg.reddit_config.user_agent,
            )
            tools.extend(create_reddit_tools(reddit))

    return tools