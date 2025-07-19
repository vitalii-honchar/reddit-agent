from logging import exception

from praw import Reddit
from praw.models import Submission, Comment
from .models import SearchQuery, RedditSubmission, SearchResult, SubmissionFilter
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage
from datetime import datetime
import logging

FILTER_PROMPT = """You are search assistant and your task is to classify Reddit submissions 
to include or exclude from the end search result. 
Analyze Reddit submission with comments and make a decision: include or exclude from the search result based on the filter rules.
If submission satisfies filter rules include summary of the submission in the result, if not return None.

<FILTER_RULES>
{filter_rules}
<FILTER_RULES> 
"""

class RedditSubmissionLlmComment(BaseModel):
    body: str = Field(description="The body of the comment, as Markdown.")
    created_utc: datetime = Field(description="The date the comment was created.")
    score: int = Field(description="Comment score")

class RedditSubmissionLlmFilterRequest(BaseModel):
    id: str = Field(description="Submission id")
    score: int = Field(description="Submission score")
    upvote_ratio: float = Field(description="Submission upvote ratio")
    created_utc: datetime = Field(description="Submission created time")
    title: str = Field(description="Submission title")
    selftext: str = Field(description="Submission selftext")
    comments: list[RedditSubmissionLlmComment] = Field(description="Submission comments")


class FilterResult(BaseModel):
    submission: RedditSubmission | None = Field(default=None, description="Reddit submission which matches filter rules")

class RedditToolsService:

    def __init__(self, reddit: Reddit, llm: BaseChatModel):
        self.reddit = reddit
        self.llm = llm

    def search(self, query: SearchQuery) -> SearchResult:

        subreddit = self.reddit.subreddit(query.subreddit)
        submissions = subreddit.search(query=query.query, sort=query.sort, time_filter=query.time_filter)

        res_submissions = []

        for submission in submissions:
            summarized_submission = self.__submission_matches(query.filter, submission)
            if summarized_submission:
                res_submissions.append(summarized_submission)

        return SearchResult(
            subreddit=query.subreddit,
            submissions=submissions,
        )

    def __submission_matches(self, submission_filter: SubmissionFilter, submission: Submission) -> RedditSubmission | None:
        if submission.selftext is None or len(submission.selftext.strip()) == 0:
            return None

        if submission.score < submission_filter.score:
            return None

        comments = self.__download_comments(submission)

        if len(comments) < submission_filter.num_comments:
            return None

        return self.__analyze_submission_with_llm(submission_filter, submission, comments)

    def __analyze_submission_with_llm(
        self,
        submission_filter: SubmissionFilter,
        submission: Submission,
        comments: list[Comment]
    ) -> RedditSubmission | None:
        try:
            llm_with_structured_output = self.llm.with_structured_output(FilterResult)
            request = self.__create_reddit_submission_llm_filter_request(submission, comments)

            prompt_messages = [
                SystemMessage(content=FILTER_PROMPT.format(filter_rules=submission_filter.filter_prompt)),
                {"role": "user", "content": request.model_dump_json()}
            ]

            res = llm_with_structured_output.invoke(prompt_messages)
            if isinstance(res, FilterResult):
                return res.submission
        except Exception:
            logging.exception("Failed to analyze submission")
        return None

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

    @staticmethod
    def __create_reddit_submission_llm_filter_request(submission: Submission, comments: list[Comment]) -> RedditSubmissionLlmFilterRequest:
        return RedditSubmissionLlmFilterRequest(
            id=submission.id,
            score=submission.score,
            created_utc=submission.created_utc,
            title=submission.title,
            selftext=submission.selftext,
            comments=[RedditSubmissionLlmComment(body=c.body, created_utc=c.created_utc, score = c.score) for c in comments],
            upvote_ratio=submission.upvote_ratio,
        )
