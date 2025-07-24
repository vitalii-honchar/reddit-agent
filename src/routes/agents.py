from fastapi import APIRouter
from schemas import Agent
from uuid import UUID

router = APIRouter(prefix="/agents", tags=["agents"])

@router.get("/")
async def get_agents() -> list[Agent]:
    return [
        Agent(
            id=UUID("aec78782-6852-11f0-8ba7-5ee52574761b"),
            name="Reddit Search Agent",
            description="Searches Reddit for provided search request",
        ),
    ]