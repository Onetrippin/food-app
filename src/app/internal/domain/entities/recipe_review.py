from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, kw_only=True)
class RecipeReviewEntity:
    id: int
    user_id: int
    username: str
    recipe_id: int
    recipe_title: str
    rating: int
    review_text: str
    moderation_status: str
    moderation_comment: str
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime
