from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

SearchSort = Literal["relevance", "hot", "top", "new"]
SearchTimeFilter = Literal["all", "day", "hour", "month", "week", "year"]

class SubmissionFilter(BaseModel):
    score: int = Field(description="Minimal reddit submission score to include post in the result")
    num_comments: int = Field(description="Minimal number of comments to include in the result")
    filter_prompt: str = Field(description="Filter rules for LLM to filter post based on the value which post should provide for the whole search process")

class SearchQuery(BaseModel):
    subreddit: str = Field(description="Subreddit name")
    query: str = Field(description="Text search query")
    sort: SearchSort = Field(description="Sort order")
    time_filter: SearchTimeFilter = Field(description="Time filter")
    filter: SubmissionFilter = Field(description="Reddit submissions filter")

class RedditSubmission(BaseModel):
    id: str = Field(description="Submission id")
    summary: str = Field(max_length=256, description="Submission summary")
    comments_summary: str = Field(max_length=256, description="Submission comments summary")
    score: int = Field(description="Submission score")
    num_comments: int = Field(description="Number of comments")
    created_utc: datetime = Field(description="Submission created time")
    upvote_ratio: float = Field(description="Submission upvote ratio")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SearchResult(BaseModel):
    subreddit: str = Field(description="Subreddit name")
    submissions: list[RedditSubmission] = Field(default=[], description="Reddit submissions which matched a search query")
