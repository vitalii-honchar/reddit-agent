from typing import Callable

import praw
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

from config import Config
from search_agent.models import CreateSearchAgentCommand, SearchResult
from search_agent.tool import create_reddit_tools
import logging

logger = logging.getLogger(__name__)

SEARCH_AGENT_PROMPT = """You are a search agent. Your mission: research provided topic by a user by using all possible tools.

## Core Directive
NEVER stop searching until you've hit actual tool rate limits or exhausted every reasonable search angle. "No results found" means try a different approach, not give up.

## Search Strategy
1. **Diversify queries**: Use synonyms, related terms, different phrasings
2. **Vary scope**: Go broad, then narrow; try different platforms/sources
3. **Multiple angles**: Technical terms + casual language + industry jargon
4. **Iterative refinement**: Use results from one search to inform the next
5. **Cross-reference**: Validate findings across multiple sources

## Search Persistence Rules
- If initial search yields poor results → reformulate and try again
- If you find partial matches → dig deeper with more specific queries  
- If rate limited on one tool → switch to other available search methods
- If no results → question your search terms and try completely different keywords
- Keep searching until you either find comprehensive results OR hit hard tool limits

## Response Requirements
- Document your search strategy and iterations
- Explain why you chose specific search terms
- If you hit limitations, clearly state what tools/limits prevented further searching
- Provide confidence levels based on search thoroughness

## Failure Conditions
Only declare search complete when:
- Tool rate limits reached
- All reasonable search variations exhausted
- Comprehensive results obtained across multiple sources

Be relentless. Mediocre search results are not acceptable.

If you didn't find anything, don't imagine a result. Instead return an empty result.

# Definition of Done
- Search must yield at least 5 relevant findings

<BEHAVIOR>
{behavior}
</BEHAVIOR>
"""

def execute_search(cfg: Config, cmd: CreateSearchAgentCommand) -> SearchResult:
    agent = create_react_agent(
        model=cfg.llm,
        tools=_create_tools(cfg, cmd),
        response_format=SearchResult,
        prompt=SEARCH_AGENT_PROMPT.format(behavior=cmd.behavior),
    )

    messages = [HumanMessage(cmd.search_query)]
    input = {"messages": messages}

    for event in agent.stream(input, stream_mode='values'):
        logger.info("Event received: %s", event)
        res = event

    return res['value']

def _create_tools(cfg: Config, cmd: CreateSearchAgentCommand) -> list[Callable]:
    tools = []

    for search_type in cmd.search_types:
        if search_type == "reddit":
            reddit = praw.Reddit(
                client_id=cfg.reddit_config.client_id,
                client_secret=cfg.reddit_config.client_secret,
                user_agent=cfg.reddit_config.user_agent,
            )
            tools.extend(create_reddit_tools(reddit, cfg.llm))

    return tools