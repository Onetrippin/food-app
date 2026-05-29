from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, kw_only=True)
class RecipeReviewEntity:
    user_id: int
    username: str
    recipe_id: int
    rating: int
    review_text: str
    created_at: datetime
    updated_at: datetime
