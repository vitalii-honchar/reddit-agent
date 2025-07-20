"""Integration test for search agent finding marketing opportunities for indie projects."""
from search_agent.search_agent import execute_search
from search_agent.models import CreateSearchAgentCommand, SearchResult
from config import Config


class TestSearchAgentIntegration:
    """Integration tests for search agent functionality."""

    def test_search_indie_project_marketing_opportunities(self, config: Config):
        """Test searching for marketing opportunities for indie projects with strict restrictions."""
        # given
        command = CreateSearchAgentCommand(
            behavior="""You are searching for marketing opportunities specifically for indie projects.
            
            Focus on:
            - Subreddits where indie developers and creators share their work
            - Communities discussing indie project marketing strategies
            - Posts about promoting indie games, apps, or creative projects
            - Marketing channels and strategies that work for small budgets
            - Community building for indie creators
            
            Strict restrictions:
            - Only include posts with at least 10 upvotes and 5 comments
            - Focus on actionable marketing advice, not just general discussion
            - Prioritize recent posts (within last month)
            - Exclude spam, self-promotion without value, or irrelevant content
            - Look for posts with practical tips, case studies, or success stories""",
            search_query="marketing opportunities for indie projects and small creators",
            search_types={"reddit"}
        )

        # when
        result = execute_search(config, command)

        # then
        assert isinstance(result, SearchResult)
        assert len(result.reddit_search_results) >= 1, "Should find at least one Reddit search result"
        
        # Check that we have results with findings
        total_findings = sum(len(search_result.submissions) for search_result in result.reddit_search_results)
        assert total_findings == 5, f"Expected exactly 5 findings, but got {total_findings}"
        
        # Verify quality of findings
        for search_result in result.reddit_search_results:
            for submission in search_result.submissions:
                assert submission.score >= 10, f"Submission {submission.id} has score {submission.score}, expected >= 10"
                assert submission.num_comments >= 5, f"Submission {submission.id} has {submission.num_comments} comments, expected >= 5"
                assert len(submission.summary) >= 500, f"Submission {submission.id} summary too short"
                assert len(submission.comments_summary) >= 500, f"Submission {submission.id} comments summary too short"