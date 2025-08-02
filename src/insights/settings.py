from app.settings import BaseAppSettings


class InsightsConfig(BaseAppSettings):
    """Configuration for Insights module"""
    agent_api_base_url: str
    insights_scheduler_timeout: int = 3600 * 24 * 7
    scheduler_enabled: bool = True