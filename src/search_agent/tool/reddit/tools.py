
from praw import Reddit
from praw.models import Submission, Comment
from .models import SearchQuery, RedditSubmission, SearchResult, RedditSubmissionComment
from langchain_core.tools import tool
from datetime import datetime
from typing import Callable
import logging

class RedditToolsService:

    def __init__(self, reddit: Reddit):
        self.reddit = reddit

    def search(self, query: SearchQuery) -> SearchResult:
        logging.info(f"Searching reddit: query = {query}")
        subreddit = self.reddit.subreddit(query.subreddit)
        submissions = subreddit.search(query=query.query, sort=query.sort, time_filter=query.time_filter)

        res_submissions = []

        for submission in submissions:
            if len(res_submissions) >= query.limit:
                break
            summarized_submission = self.__submission_matches(query, submission)
            if summarized_submission:
                res_submissions.append(summarized_submission)

        logging.info(f"Found Reddit submissions: submissions = {len(res_submissions)}")

        return SearchResult(
            subreddit=query.subreddit,
            submissions=res_submissions,
        )

    def __submission_matches(self, query: SearchQuery, submission: Submission) -> RedditSubmission | None:
        # Basic content checks
        if submission.selftext is None or len(submission.selftext.strip()) == 0:
            return None

        submission_filter = query.filter
        if len(submission.selftext.strip()) < submission_filter.min_content_length:
            return None
            
        if len(submission.title.strip()) < submission_filter.min_title_length:
            return None

        # Score and engagement checks
        if submission.score < submission_filter.min_score:
            return None
            
        if submission.upvote_ratio < submission_filter.min_upvote_ratio:
            return None

        # Age check
        submission_age_days = (datetime.now() - datetime.fromtimestamp(submission.created_utc)).days
        if submission_age_days > submission_filter.max_days_old:
            return None

        # Flair check
        if submission.link_flair_text and submission_filter.excluded_flairs:
            if any(flair.lower() in submission.link_flair_text.lower() for flair in submission_filter.excluded_flairs):
                return None

        # Keyword checks
        content_text = (submission.title + " " + submission.selftext).lower()
        
        # Required keywords check
        if submission_filter.required_keywords:
            if not all(keyword.lower() in content_text for keyword in submission_filter.required_keywords):
                return None
                
        # Excluded keywords check
        if submission_filter.excluded_keywords:
            if any(keyword.lower() in content_text for keyword in submission_filter.excluded_keywords):
                return None

        # Comments check
        comments = self.__download_comments(submission)
        if len(comments) < submission_filter.min_comments:
            return None

        # Valuable comments ratio check
        valuable_comments = [c for c in comments if c.score >= submission_filter.min_comment_score_threshold]
        if len(comments) > 0:
            valuable_ratio = len(valuable_comments) / len(comments)
            if valuable_ratio < submission_filter.min_valuable_comments_ratio:
                return None

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
    def __download_comments(submission: Submission) -> list[Comment]:
        try:
            # submission.comments.replace_more(limit=None)
            
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
    def reddit_search(
        query: SearchQuery
    ) -> str:
        """
        Search Reddit for posts matching specific criteria.

        Args:
            query: Search query.
        Returns:
            SearchResult as JSON containing matching Reddit submissions
        """
        return reddit_service.search(query).model_dump_json()
    
    return reddit_search

def create_reddit_tools(reddit: Reddit) -> list[Callable]:
    svc = RedditToolsService(reddit)
    return [
        create_reddit_search_tool(svc),
    ]