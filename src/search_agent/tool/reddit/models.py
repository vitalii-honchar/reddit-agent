from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

class SubmissionFilter(BaseModel):
    min_score: int = Field(description="Minimal reddit submission score to include post in the result")
    min_comments: int = Field(description="Minimal number of comments to include in the result")
    filter_prompt: str = Field(description="Filter rules for LLM to filter post based on the value which post should provide for the whole search process")

class SearchQuery(BaseModel):
    subreddit: str = Field(description="Subreddit name")
    query: str = Field(description="Text search query")
    sort: Literal["relevance", "hot", "top", "new"] = Field(default="top", description="Sort order")
    time_filter: Literal["all", "day", "hour", "month", "week", "year"] = Field(default="month",description="Time filter")
    filter: SubmissionFilter = Field(description="Reddit submissions filter")
    limit: int = Field(default=25, description="Number of results to return")

class RedditSubmission(BaseModel):
    id: str = Field(description="Submission id")
    summary: str = Field(min_length=500, max_length=512, description="Submission summary")
    comments_summary: str = Field(min_length=500, max_length=512, description="Submission comments summary")
    score: int = Field(description="Submission score")
    num_comments: int = Field(description="Number of comments")
    created_utc: datetime = Field(description="Submission created time")
    upvote_ratio: float = Field(description="Submission upvote ratio")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class SearchResult(BaseModel):
    subreddit: str = Field(description="Subreddit name")
    submissions: list[RedditSubmission] = Field(default=[], description="Reddit submissions which matched a search query")
