from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, kw_only=True)
class RecipeReportEntity:
    id: int
    user_id: int
    username: str
    recipe_id: int
    recipe_title: str
    reason: str
    description: str
    status: str
    moderation_comment: str
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime
