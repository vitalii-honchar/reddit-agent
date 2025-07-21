from typing import Literal

from pydantic import BaseModel, Field
from search_agent.tool import RedditSubmissionSearchResult

class SearchResult(BaseModel):
    reddit_search_results: list[RedditSubmissionSearchResult] = Field(
        default=[],
        description="List of subreddit search results."
    )

class CreateSearchAgentCommand(BaseModel):
    behavior: str = Field(
        description="High-level mission statement that guides the agent’s tone and approach. ",
        examples=[
            "Uncover revenue-driving tactics used by top SaaS founders.",
            "Identify growth tactics used by indie game devs",
            "Deep-dive competitive analysis on emerging AI startups"
        ]
    )
    search_query: str = Field(
        description=(
            "The exact keyword or phrase to kick off the search. "
            "Should be concise but specific—include product names, metrics, or niche topics."
        ),
        examples=["indie game marketing strategies Twitter engagement"]
    )
    search_types: set[Literal["reddit"]] = Field(
        description=(
            "Set of platforms to search. Currently only supports 'reddit', "
            "but designed for future expansion (e.g. 'twitter', 'stack_overflow')."
        ),
        examples=["reddit"]
    )
    min_results: int = Field(
        default=5,
        ge=1,
        description=(
            "Minimum number of search results to return."
            "If fewer are found, the agent will keep iterating until this threshold is met or tools are exhausted."
        ),
        examples=[5]
    )