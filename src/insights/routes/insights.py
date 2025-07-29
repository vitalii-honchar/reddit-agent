from typing import Sequence

from fastapi import APIRouter

from insights.models.insight import Insight

router = APIRouter(prefix="/insights", tags=["insights"])

@router.get("/")
def insights() -> Sequence[Insight]:
    pass