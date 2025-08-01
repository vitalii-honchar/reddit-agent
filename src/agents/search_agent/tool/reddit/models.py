from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class SubmissionFilter(BaseModel):
    min_score: int = Field(
        default=5,
        description="Minimal reddit submission score to include post in the result",
        examples=[5])
    min_comments: int = Field(
        default=5,
        description="Minimal number of comments to include in the result",
        examples=[5])
    min_upvote_ratio: float = Field(default=0.7, description="Minimal upvote ratio (0.0-1.0)", examples=[0.7])
    max_days_old: int = Field(default=30, description="Maximum age of submission in days", examples=[30])
    min_title_length: int = Field(default=10, description="Minimum title length in characters", examples=[10])
    min_content_length: int = Field(default=50, description="Minimum content length in characters", examples=[50])
    required_keywords: list[str] = Field(
        default=[],
        description="Keywords that must appear in title or content (case insensitive)",
        examples=["python"])
    excluded_keywords: list[str] = Field(
        default=[],
        description="Keywords that exclude post if found in title or content (case insensitive)",
        examples=["test"])
    excluded_flairs: list[str] = Field(default=[], description="Post flairs to exclude (case insensitive)",
                                       examples=["python"])
    min_comment_score_threshold: int = Field(
        default=2,
        description="Minimum score for comments to be considered valuable",
        examples=[2])
    min_valuable_comments_ratio: float = Field(
        default=0.3,
        description="Minimum ratio of valuable comments (score >= threshold)",
        examples=[0.3])
    filter_prompt: str = Field(
        default="",
        description="Legacy field - kept for backward compatibility but not used in heuristic filtering",
        examples=["python"])


class SearchQuery(BaseModel):
    subreddit: str = Field(description="The name of the subreddit", examples=["python", "IndieHackers"])
    query: str = Field(description="Text search query")
    sort: Literal["relevance", "hot", "top", "new"] = Field(default="top", description="Sort order")
    time_filter: Literal["all", "day", "hour", "month", "week", "year"] = Field(default="month",
                                                                                description="Time filter")
    filter: SubmissionFilter = Field(description="Reddit submissions filter")
    limit: int = Field(default=25, description="Number of results to return")


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
