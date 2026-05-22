from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, kw_only=True)
class AuthorApplicationEntity:
    user_id: int
    motivation: str
    status: str
    subscription_price: Decimal
    subscription_currency: str
    is_subscription_enabled: bool
    review_comment: str
    reviewed_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
