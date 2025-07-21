from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class SubmissionFilter(BaseModel):
    min_score: int = Field(description="Minimal reddit submission score to include post in the result")
    min_comments: int = Field(description="Minimal number of comments to include in the result")
    min_upvote_ratio: float = Field(default=0.7, description="Minimal upvote ratio (0.0-1.0)")
    max_days_old: int = Field(default=30, description="Maximum age of submission in days")
    min_title_length: int = Field(default=10, description="Minimum title length in characters")
    min_content_length: int = Field(default=50, description="Minimum content length in characters")
    required_keywords: list[str] = Field(default=[],
                                         description="Keywords that must appear in title or content (case insensitive)")
    excluded_keywords: list[str] = Field(default=[],
                                         description="Keywords that exclude post if found in title or content (case insensitive)")
    excluded_flairs: list[str] = Field(default=[], description="Post flairs to exclude (case insensitive)")
    min_comment_score_threshold: int = Field(default=2,
                                             description="Minimum score for comments to be considered valuable")
    min_valuable_comments_ratio: float = Field(default=0.3,
                                               description="Minimum ratio of valuable comments (score >= threshold)")
    filter_prompt: str = Field(default="",
                               description="Legacy field - kept for backward compatibility but not used in heuristic filtering")


class SearchQuery(BaseModel):
    subreddit: str = Field(description="The name of the subreddit", examples=["python", "IndieHackers"])
    query: str = Field(description="Text search query")
    sort: Literal["relevance", "hot", "top", "new"] = Field(default="top", description="Sort order")
    time_filter: Literal["all", "day", "hour", "month", "week", "year"] = Field(default="month",
                                                                                description="Time filter")
    filter: SubmissionFilter = Field(description="Reddit submissions filter")
    limit: int = Field(default=25, description="Number of results to return")


class RedditSubmissionSearchResult(BaseModel):
    id: str = Field(description="The unique ID of the Reddit submission", examples=["g5w4q1"])
    subreddit: str = Field(description="The name of the subreddit", examples=["python", "IndieHackers"])
    summary: str = Field(
        min_length=80,
        max_length=150,
        description=(
            "2–3 concise sentences (80–150 chars) capturing the single most strategic "
            "tactic or metric related to the original search query. "
            "Include a numeric or qualitative result (e.g. “+30% conversions,” “5K users in 2 weeks”). "
            "Omit all background context, anecdotes, or filler—every word must drive value."
        ),
        examples=[
            "Posted 3×/week on Twitter & IG → grew followers by 40% in 2 months.",
        ]
    )
    comments_summary: str = Field(
        max_length=240,
        description=(
            "Up to 3 bullet points (each ≤80 chars) starting with an action verb, "
            "highlighting only tactics or warnings that directly advance the original query. "
            "Skip off-topic chatter or anecdotes."
        ),
        examples=[
            "- Use #IndieDev + #GameDev → doubled post engagement.",
            "- Collaborate with 2 other devs each week → +15% reach.",
        ]
    )
    score: int = Field(description="The submission’s score (upvotes minus downvotes).")
    num_comments: int = Field(description="Total number of comments on the submission.")
    created_utc: datetime = Field(description="Submission creation timestamp in UTC (ISO 8601).")
    upvote_ratio: float = Field(description="Fraction of upvotes out of total votes.")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class RedditSubmissionComment(BaseModel):
    score: int = Field(description="The comment score (upvotes minus downvotes).")
    body: str = Field(description="The comment body")


class RedditSubmission(BaseModel):
    id: str = Field(description="The unique ID of the Reddit submission", examples=["g5w4q1"])
    subreddit: str = Field(description="The name of the subreddit", examples=["python", "IndieHackers"])
    title: str = Field(description="Reddit submission title")
    selftext: str = Field(
        description="Reddit submission selftext which matches sarch query",
    )
    comments: list[RedditSubmissionComment] = Field(
        description="Top 5 Reddit submission comments",
    )
    score: int = Field(description="The submission’s score (upvotes minus downvotes).")
    num_comments: int = Field(description="Total number of comments on the submission.")
    created_utc: datetime = Field(description="Submission creation timestamp in UTC (ISO 8601).")
    upvote_ratio: float = Field(description="Fraction of upvotes out of total votes.")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class SearchResult(BaseModel):
    subreddit: str = Field(description="The name of the subreddit", examples=["python", "IndieHackers"])
    submissions: list[RedditSubmission] = Field(
        default=[],
        description="List of submissions matching the query"
    )
