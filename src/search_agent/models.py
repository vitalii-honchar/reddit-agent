from typing import Literal

from pydantic import BaseModel, Field
from search_agent.tool import RedditSearchResult

class SearchResult(BaseModel):
    reddit_search_results: list[RedditSearchResult] = Field(
        default=[],
        description=(
            "List of subreddit search results. "
            "Each entry must include only subreddits with one or more submissions; "
            "any subreddit with an empty `submissions` list will be omitted."
        )
    )

class CreateSearchAgentCommand(BaseModel):
    behavior: str = Field(description="The behavior of the search agent")
    search_query: str = Field(description="The search query")
    search_types: set[Literal["reddit"]] = Field(description="Search types")