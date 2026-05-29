from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, kw_only=True)
class RecipeReportEntity:
    user_id: int
    recipe_id: int
    reason: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime
