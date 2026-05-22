from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, kw_only=True)
class RecipePurchaseEntity:
    user_id: int
    recipe_id: int
    purchased_at: datetime
