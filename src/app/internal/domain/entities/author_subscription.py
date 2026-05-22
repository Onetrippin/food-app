from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(slots=True, kw_only=True)
class AuthorSubscriptionEntity:
    subscriber_id: int
    author_id: int
    amount: Decimal
    currency: str
    payment_method_id: str
    started_at: datetime
    expires_at: datetime
    is_active: bool
