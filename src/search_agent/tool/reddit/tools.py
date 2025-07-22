
import asyncpraw
from asyncpraw.models import Submission, Comment
from .models import SearchQuery, RedditSubmission, SearchResult, RedditSubmissionComment, SubmissionFilter
from langchain_core.tools import tool
from datetime import datetime
from typing import Callable, Protocol
from abc import ABC, abstractmethod
import logging

class SubmissionFilterStrategy(ABC):
    """Abstract base class for submission filtering strategies."""
    
    @abstractmethod
    async def filter(self, submission: Submission, submission_filter: SubmissionFilter, **kwargs) -> bool:
        """Return True if submission passes this filter, False otherwise."""
        pass


class ContentLengthFilter(SubmissionFilterStrategy):
    """Filters submissions based on title and content length."""
    
    async def filter(self, submission: Submission, submission_filter: SubmissionFilter, **kwargs) -> bool:
        if submission.selftext is None or len(submission.selftext.strip()) == 0:
            return False
        
        if len(submission.selftext.strip()) < submission_filter.min_content_length:
            return False
            
        if len(submission.title.strip()) < submission_filter.min_title_length:
            return False
            
        return True


class ScoreFilter(SubmissionFilterStrategy):
    """Filters submissions based on score and upvote ratio."""
    
    async def filter(self, submission: Submission, submission_filter: SubmissionFilter, **kwargs) -> bool:
        if submission.score < submission_filter.min_score:
            return False
            
        if submission.upvote_ratio < submission_filter.min_upvote_ratio:
            return False
            
        return True


class AgeFilter(SubmissionFilterStrategy):
    """Filters submissions based on age."""
    
    async def filter(self, submission: Submission, submission_filter: SubmissionFilter, **kwargs) -> bool:
        submission_age_days = (datetime.now() - datetime.fromtimestamp(submission.created_utc)).days
        return submission_age_days <= submission_filter.max_days_old


class FlairFilter(SubmissionFilterStrategy):
    """Filters submissions based on excluded flairs."""
    
    async def filter(self, submission: Submission, submission_filter: SubmissionFilter, **kwargs) -> bool:
        if submission.link_flair_text and submission_filter.excluded_flairs:
            return not any(flair.lower() in submission.link_flair_text.lower() 
                          for flair in submission_filter.excluded_flairs)
        return True


class KeywordFilter(SubmissionFilterStrategy):
    """Filters submissions based on required and excluded keywords."""
    
    async def filter(self, submission: Submission, submission_filter: SubmissionFilter, **kwargs) -> bool:
        content_text = (submission.title + " " + submission.selftext).lower()
        
        # Required keywords check
        if submission_filter.required_keywords:
            if not all(keyword.lower() in content_text for keyword in submission_filter.required_keywords):
                return False
                
        # Excluded keywords check
        if submission_filter.excluded_keywords:
            if any(keyword.lower() in content_text for keyword in submission_filter.excluded_keywords):
                return False
                
        return True


class CommentsFilter(SubmissionFilterStrategy):
    """Filters submissions based on comments count and quality."""
    
    async def filter(self, submission: Submission, submission_filter: SubmissionFilter, **kwargs) -> bool:
        comments = kwargs.get('comments', [])
        
        if len(comments) < submission_filter.min_comments:
            return False

        # Valuable comments ratio check
        valuable_comments = [c for c in comments if c.score >= submission_filter.min_comment_score_threshold]
        if len(comments) > 0:
            valuable_ratio = len(valuable_comments) / len(comments)
            if valuable_ratio < submission_filter.min_valuable_comments_ratio:
                return False
                
        return True


class SubmissionFilterManager:
    """Manages and applies multiple filter strategies."""
    
    def __init__(self):
        self.filters = [
            ContentLengthFilter(),
            ScoreFilter(),
            AgeFilter(),
            FlairFilter(),
            KeywordFilter(),
            CommentsFilter(),
        ]
    
    async def apply_filters(self, submission: Submission, submission_filter: SubmissionFilter, comments: list) -> bool:
        """Apply all filters to a submission. Returns True if all filters pass."""
        for filter_strategy in self.filters:
            if not await filter_strategy.filter(submission, submission_filter, comments=comments):
                return False
        return True


class RedditToolsService:

    def __init__(self, reddit: asyncpraw.Reddit):
        self.reddit = reddit
        self.filter_manager = SubmissionFilterManager()

    async def search(self, query: SearchQuery) -> SearchResult:
        logging.info(f"Searching reddit: query = {query}")
        subreddit = await self.reddit.subreddit(query.subreddit)
        submissions = subreddit.search(query=query.query, sort=query.sort, time_filter=query.time_filter)

        res_submissions = []

        async for submission in submissions:
            if len(res_submissions) >= query.limit:
                break
            summarized_submission = await self.__submission_matches(query, submission)
            if summarized_submission:
                res_submissions.append(summarized_submission)

        logging.info(f"Found Reddit submissions: submissions = {len(res_submissions)}")

        return SearchResult(
            subreddit=query.subreddit,
            submissions=res_submissions,
        )

    async def __submission_matches(self, query: SearchQuery, submission: Submission) -> RedditSubmission | None:
        # Load submission data first
        await submission.load()
        
        # Download comments early as they're needed for filtering
        comments = await self.__download_comments(submission)
        
        # Apply all filters using the strategy pattern
        if not await self.filter_manager.apply_filters(submission, query.filter, comments):
            return None

        # If we reach here, all filters passed - create and return the result
        valuable_comments = [c for c in comments if c.score >= query.filter.min_comment_score_threshold]
        top_5_comments = sorted(valuable_comments, key=lambda c: c.score, reverse=True)[:5]

        return RedditSubmission(
            id=submission.id,
            subreddit=query.subreddit,
            title=submission.title,
            selftext=submission.selftext,
            comments=[RedditSubmissionComment(score=c.score, body=c.body) for c in top_5_comments],
            score=submission.score,
            num_comments=submission.num_comments,
            created_utc=datetime.fromtimestamp(submission.created_utc),
            upvote_ratio=submission.upvote_ratio
        )

    @staticmethod
    async def __download_comments(submission: Submission) -> list[Comment]:
        try:
            all_comments = []
            for comment in submission.comments.list():
                if isinstance(comment, Comment):
                    all_comments.append(comment)
            
            return all_comments
            
        except Exception:
            logging.exception(f"Failed to download comments for submission {submission.id}")
            return []


def create_reddit_search_tool(reddit_service: RedditToolsService) -> Callable:
    """Create a LangGraph-compatible tool for Reddit search."""
    
    @tool("reddit_search")
    async def reddit_search(
        query: SearchQuery
    ) -> str:
        """
        Search Reddit for submissions matching detailed criteria and serialize to JSON.

        Steps:
          1. Query the specified subreddit with `query.query`, `query.sort`, and `query.time_filter`.
          2. For each submission, enforce:
             • Minimum title and selftext length
             • Score ≥ `query.filter.min_score`
             • Upvote ratio ≥ `query.filter.min_upvote_ratio`
             • Age ≤ `query.filter.max_days_old` days
             • No excluded flairs if `query.filter.excluded_flairs` is set
             • Presence of all `required_keywords` and absence of any `excluded_keywords`
          3. Download all comments, require ≥ `query.filter.min_comments`
          4. Compute ratio of comments ≥ `min_comment_score_threshold`, require ≥ `min_valuable_comments_ratio`
          5. Select top 5 comments by score and include their `score` and `body`
          6. Stop once `query.limit` valid submissions are collected

        Args:
            query (SearchQuery):
                - subreddit (str): e.g. 'r/python'
                - query (str): search keywords
                - sort (str): 'relevance', 'hot', etc.
                - time_filter (str): 'all', 'day', 'week', etc.
                - limit (int): max submissions to return
                - filter (SubmissionFilter): detailed filter parameters

        Returns:
            str: A JSON string matching the `SearchResult` model with fields:
                {
                  "subreddit": str,
                  "submissions": [
                    {
                      "id": str,
                      "title": str,
                      "selftext": str,
                      "comments": [{"score": int, "body": str}, …],
                      "score": int,
                      "num_comments": int,
                      "created_utc": "2025-07-20T14:23:00Z",
                      "upvote_ratio": float
                    },
                    …
                  ]
                }
        """
        try:
            result = await reddit_service.search(query)
            return result.model_dump_json()
        except Exception as e:
            logging.exception(f"Failed to get Reddit search results: query = {query}")
            raise e
    
    return reddit_search

def create_reddit_tools(reddit: asyncpraw.Reddit) -> list[Callable]:
    svc = RedditToolsService(reddit)
    return [
        create_reddit_search_tool(svc),
    ]