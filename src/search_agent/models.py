from typing import Literal

from pydantic import BaseModel, Field
from search_agent.tool import RedditSearchResult

class SearchResult(BaseModel):
    reddit_search_results: list[RedditSearchResult] = Field(default=[], description="Reddit search results")

class CreateSearchAgentCommand(BaseModel):
    behavior: str = Field(description="The behavior of the search agent")
    search_query: str = Field(description="The search query")
    search_types: set[Literal["reddit"]] = Field(description="Search types")