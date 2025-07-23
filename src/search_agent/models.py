from typing import Literal

from pydantic import BaseModel, Field
from search_agent.tool import RedditSubmissionSearchResult


class Finding(BaseModel):
    source: Literal["reddit"] = Field(
        description="Platform where this finding was discovered. Currently only 'reddit' supported.",
        examples=["reddit"]
    )
    source_id: str = Field(
        description="Unique identifier from the source platform (e.g., Reddit post ID).",
        examples=["t3_g5w4q1", "h8k9m2n"]
    )
    title: str = Field(
        description="Original title or headline of the source content.",
        examples=[
            "How I grew my SaaS to $10k MRR in 6 months",
            "Failed 3 times before finding product-market fit"
        ]
    )
    summary: str = Field(
        min_length=80,
        max_length=150,
        description=(
            "2-3 sentences capturing the core actionable insight. "
            "Must include specific tactics and measurable outcomes. "
            "Skip all context/stories—focus only on what worked and the results."
        ),
        examples=[
            "Cold DM'd 50 potential customers daily on LinkedIn. Booked 3-5 calls/week → closed $10k MRR in 6 months.",
            "Launched on Product Hunt every 2 weeks with feature updates. Each launch brought 200-500 signups."
        ]
    )
    action_items: list[str] = Field(
        max_length=3,
        description=(
            "Bullet points of specific, implementable tactics extracted from the content. "
            "Each must start with an action verb and be ≤80 chars. "
            "Include only tactics that directly support the main insight."
        ),
        examples=[
            ["Use 'founder' in LinkedIn DMs → 3x response rate",
             "Follow up exactly 48hrs later → +40% conversions",
             "Share customer wins as social proof in pitch"],
            ["Submit to /r/SideProject on Tuesdays at 9am EST",
             "Cross-post to IndieHackers within 1 hour",
             "Engage with 5 comments before posting"]
        ]
    )
    relevance_score: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "How well this finding matches the original search query. "
            "1.0 = perfect match with actionable tactics, "
            "0.5 = partially relevant or missing specifics, "
            "0.0 = completely off-topic."
        ),
        examples=[0.95, 0.7, 0.3]
    )


class SearchMetadata(BaseModel):
    total_searches: int = Field(
        ge=1,
        description="Total number of search queries executed across all platforms.",
        examples=[12, 25, 7]
    )
    searches_by_source: dict[str, int] = Field(
        description="Breakdown of searches performed on each platform.",
        examples=[
            {"reddit": 12},
            {"reddit": 8, "twitter": 4},
            {"reddit": 15, "stack_overflow": 10}
        ]
    )
    filtering_stats: dict[str, int] = Field(
        description=(
            "Quality filtering statistics showing accepted vs rejected content. "
            "Keys typically include 'accepted', 'rejected', 'low_quality', 'off_topic', etc."
        ),
        examples=[
            {"accepted": 5, "rejected": 20, "low_quality": 15, "off_topic": 5},
            {"accepted": 8, "rejected": 40, "promotional": 10, "too_old": 12, "no_specifics": 18}
        ]
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "Agent's confidence in result completeness and quality. "
            "1.0 = found many high-quality, diverse sources; "
            "0.5 = adequate but limited findings; "
            "0.0 = results are sparse or low quality."
        ),
        examples=[0.85, 0.6, 0.3]
    )


class SearchResult(BaseModel):
    reddit_search_results: list[RedditSubmissionSearchResult] = Field(
        default=[],
        description="Raw Reddit search results before processing into unified findings."
    )
    findings: list[Finding] = Field(
        description=(
            "Curated list of high-quality, actionable insights from all sources. "
            "Each finding represents a validated tactic with measurable outcomes."
        )
    )
    metadata: SearchMetadata = Field(
        description="Search execution statistics and quality metrics for transparency and debugging."
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
    recursion_limit: int = Field(default=25, description="Maximum recursion limit.", examples=[25, 50])
