import logging
import random
import uuid

from insights.agentapi_client.fast_api_client.models import AgentConfigurationUpdate, AgentConfigurationUpdateData
from insights.services import AgentAPIService
from logging import Logger

configs = [
    AgentConfigurationUpdate(
        id=uuid.UUID("1b676236-6d21-11f0-9248-5ee52574761b"),
        agent_type="search_agent",
        data=AgentConfigurationUpdateData.from_dict({
            "behavior": """You are researching actual SaaS products that have launched and their specific details.
               Focus on:
               - Named SaaS products with launch details and current revenue/user numbers
               - Specific tools/platforms that founders built and launched (with URLs/names)
               - "I launched X and here's what happened" posts with product details
               - Product demos, launch announcements, and launch day results
               - Actual product names, features, pricing, and customer testimonials

               For each finding, identify opportunities for indie hackers:
               - Underserved niches or market gaps mentioned in discussions
               - Features users request but aren't available in existing products
               - Pricing models or customer segments that could be better served
               - Technical approaches that could be simplified or improved
               - Distribution channels or marketing tactics that worked well

               Strict restrictions:
               - Only include posts with at least 20 upvotes and 10 comments
               - Must mention specific product name, URL, or clear product description
               - Must include launch metrics (users, revenue, signups, conversions)
               - Prioritize posts with "Show HN", "I built", "I launched" format
               - Exclude generic advice posts without actual product mentions
               - Look for product screenshots, feature lists, or demo links""",
            "search_query": "I launched SaaS product built tool Show HN demo revenue",
            "search_types": ["reddit"],
        }),
    ),
    AgentConfigurationUpdate(
        id=uuid.UUID("1f866f9a-6de6-11f0-9cdb-5ee52574761b"),
        agent_type="search_agent",
        data=AgentConfigurationUpdateData.from_dict({
            "behavior": """You are researching actual cybersecurity products launched by indie hackers and small teams.
               Focus on:
               - Named security tools with product URLs, demos, or GitHub repos
               - Specific vulnerability scanners, pen-testing tools, security platforms built by indies
               - "I built a security tool" posts with product names and features
               - Actual cybersecurity SaaS products with pricing and customer counts
               - Security compliance tools, audit platforms, monitoring solutions with launch stories

               For each finding, identify opportunities for indie hackers:
               - Security pain points that existing tools don't address well
               - Simpler alternatives to complex enterprise security solutions
               - Niche security problems specific to certain industries or company sizes
               - Open source security tools that could have commercial versions
               - Integration gaps between existing security tools

               Strict restrictions:
               - Only include posts with at least 20 upvotes and 10 comments
               - Must mention specific product name, URL, or detailed product description
               - Must include launch metrics (users, revenue, downloads, GitHub stars)
               - Prioritize posts showing actual product screenshots or demos
               - Exclude generic security advice without product mentions
               - Look for "Show HN", "I launched", "I built" security product posts""",
            "search_query": "I built security tool launched cybersecurity product Show HN vulnerability scanner",
            "search_types": ["reddit"],
        }),
    ),
    AgentConfigurationUpdate(
        id=uuid.UUID("2a64ea22-6de6-11f0-9bbe-5ee52574761b"),
        agent_type="search_agent",
        data=AgentConfigurationUpdateData.from_dict({
            "behavior": """You are researching actual product validation experiments and launch case studies by indie hackers.
               Focus on:
               - Specific products with detailed validation stories (survey results, landing page tests, pre-orders)
               - Named failed products with exact failure reasons and metrics
               - Product Hunt launches with specific traffic/conversion numbers and product names
               - A/B test results for actual landing pages with before/after data
               - Community launch stories mentioning specific products and their outcomes

               For each finding, identify opportunities for indie hackers:
               - Validation methods that worked particularly well for certain types of products
               - Common failure patterns that could be avoided with better approaches
               - Underexplored markets where validation showed demand but execution failed
               - Successful validation techniques that aren't widely known or used
               - Product ideas that failed due to execution rather than market demand

               Strict restrictions:
               - Only include posts with at least 20 upvotes and 10 comments
               - Must mention specific product name or detailed product description
               - Must include actual validation numbers (survey responses, signups, conversions, revenue)
               - Prioritize posts with screenshots of metrics, landing pages, or analytics
               - Exclude generic validation advice without specific product examples
               - Look for "I validated", "failed launch", "Product Hunt results" with product details""",
            "search_query": "validated idea failed product Product Hunt launch results metrics landing page test",
            "search_types": ["reddit"],
        }),
    ),
    AgentConfigurationUpdate(
        id=uuid.UUID("3e7f2c84-6de6-11f0-8a45-5ee52574761b"),
        agent_type="search_agent",
        data=AgentConfigurationUpdateData.from_dict({
            "behavior": """You are researching actual AI products launched for customer support and service automation.
               Focus on:
               - Named AI customer support tools with product URLs and demos
               - Chatbots, helpdesk automation, and AI-powered support platforms built by founders
               - "I built an AI support tool" posts with product names and features
               - Customer service AI products with usage metrics and customer testimonials
               - Support ticket routing, AI chat assistants, and automated response systems with launch stories

               For each finding, identify opportunities for indie hackers:
               - Customer support pain points that existing AI tools don't solve well
               - Industry-specific support needs (healthcare, e-commerce, SaaS, etc.)
               - Integration gaps between popular support platforms and AI tools
               - Simpler alternatives to complex enterprise support AI solutions
               - Emerging support channels that need AI automation (social media, messaging apps)

               Strict restrictions:
               - Only include posts with at least 20 upvotes and 10 comments
               - Must mention specific product name, URL, or detailed product description
               - Must include launch metrics (customers, support ticket volume, response time improvements)
               - Prioritize posts showing actual product screenshots, demos, or customer results
               - Exclude generic AI advice without specific customer support product mentions
               - Look for "Show HN", "I launched", "I built" AI customer support posts""",
            "search_query": "AI customer support chatbot launched helpdesk automation Show HN built support tool",
            "search_types": ["reddit"],
        }),
    ),
    AgentConfigurationUpdate(
        id=uuid.UUID("4b8a5d92-6de6-11f0-9c73-5ee52574761b"),
        agent_type="search_agent",
        data=AgentConfigurationUpdateData.from_dict({
            "behavior": """You are researching actual AI products launched for Instagram creators and influencers.
               Focus on:
               - Named AI tools for Instagram content creation with product URLs and demos
               - Content scheduling, editing, analytics, and automation tools built specifically for creators
               - "I built an Instagram AI tool" posts with product names and creator testimonials
               - Creator-focused AI products with user counts, engagement metrics, and revenue numbers
               - Instagram-specific features like story templates, hashtag optimization, caption generation with launch stories

               For each finding, identify opportunities for indie hackers:
               - Creator pain points that existing AI tools don't address well
               - Underserved creator niches (micro-influencers, specific industries, new content formats)
               - Integration opportunities with Instagram's latest features and API changes
               - Simpler alternatives to expensive enterprise creator management platforms
               - Monetization gaps in the creator economy that AI could help solve

               Strict restrictions:
               - Only include posts with at least 20 upvotes and 10 comments
               - Must mention specific product name, URL, or detailed product description
               - Must include launch metrics (creator signups, engagement improvements, revenue generated)
               - Prioritize posts showing actual product screenshots, creator results, or case studies
               - Exclude generic Instagram growth advice without specific AI product mentions
               - Look for "Show HN", "I launched", "I built" Instagram AI tool posts""",
            "search_query": "Instagram AI tool creator launched influencer automation Show HN built content creation",
            "search_types": ["reddit"],
        }),
    ),
    AgentConfigurationUpdate(
        id=uuid.UUID("5c9b6e48-6de6-11f0-8e82-5ee52574761b"),
        agent_type="search_agent",
        data=AgentConfigurationUpdateData.from_dict({
            "behavior": """You are researching hidden opportunities for indie projects in unexpected Reddit communities, avoiding obvious entrepreneurial spaces.

               TARGET COMMUNITIES (focus exclusively on these):
               - r/MachineLearning, r/datascience, r/Python, r/Programming, r/WebDev, r/DevOps
               - r/Teachers, r/Professors, r/Education, r/HomeschoolRecovery
               - r/Medicine, r/Nursing, r/pharmacy, r/medicalschool, r/residency
               - r/LegalAdvice, r/law, r/paralegal, r/BigLaw
               - r/WeightLoss, r/loseit, r/Fitness, r/MealPrepSunday, r/nutrition
               - r/PersonalFinance, r/povertyfinance, r/Frugal, r/YNAB, r/financialindependence
               - r/Parenting, r/Mommit, r/daddit, r/StudentLoans, r/college
               - r/freelance, r/remotework, r/WorkFromHome, r/Bookkeeping, r/accounting
               - r/Design, r/GraphicDesign, r/UXDesign, r/webdesign, r/logodesign
               - r/gamedev, r/Unity3D, r/unrealengine, r/godot, r/indiegaming
               - r/photography, r/videography, r/VideoEditing, r/editors, r/premiere
               - r/WeAreTheMusicMakers, r/edmproduction, r/trapproduction, r/ableton

               EXPLICIT FILTER CRITERIA (MUST SKIP these patterns):
               - Any subreddit containing: entrepreneur, startup, business, investing, crypto, marketing, sales
               - Posts mentioning: "business idea", "startup", "pitch", "investor", "funding", "venture"
               - Generic rants without specific tool/process mentions
               - Posts older than 6 months
               - Posts with solutions already provided in top comments
               - Cross-posts to business/entrepreneur subreddits
               - Posts about making money online or passive income

               REQUIRED DATA POINTS for each opportunity:
               1. Problem Statement: Exact description of the pain point mentioned
               2. Current Solution Gap: Why existing tools fail (too expensive, complex, missing features)
               3. User Frequency: How often this problem occurs (daily, weekly, per project)
               4. Market Size Indicators: Number of users affected, community size, comment engagement
               5. Technical Complexity: Estimated difficulty to build a solution (simple, moderate, complex)
               6. Monetization Potential: Willingness to pay indicators from comments
               7. Competition Analysis: Existing solutions mentioned and their limitations
               8. Implementation Hints: Technical approaches suggested by users

               ENGAGEMENT THRESHOLDS:
               - Minimum 20 upvotes and 15 meaningful comments
               - At least 3 different users expressing the same frustration
               - Post must contain specific examples, not vague complaints
               - Look for phrases: "I hate having to...", "Why is there no tool for...", "I spend hours doing..."
               - Prioritize posts where users share workarounds or manual processes""",
            "search_query": "tool missing frustrated workflow automation painful process manual tedious",
            "search_types": ["reddit"],
        }),
    ),
]


class AgentConfigurationService:

    def __init__(self, agent_api_service: AgentAPIService, logger: Logger):
        self.agent_api_service = agent_api_service
        self.logger = logger

    async def migrate(self):
        self.logger.info("Migrating agent configurations: %d", len(configs))
        
        # Shuffle configs to randomize execution order
        shuffled_configs = configs.copy()
        random.shuffle(shuffled_configs)
        
        for config in shuffled_configs:
            logging.info("Migrating agent configuration: %s", config.id)
            res = await self.agent_api_service.upsert_configuration(config)
            if not res:
                raise RuntimeError(f"Failed to upsert configuration: {config.id}")

        self.logger.info("Migrated agent configurations: %d", len(configs))
