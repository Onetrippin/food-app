from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(slots=True, kw_only=True)
class PaymentEntity:
    user_id: int
    payment_type: str
    status: str
    amount: Decimal
    currency: str
    description: str
    yookassa_payment_id: str
    recipe_id: int | None = None
    author_id: int | None = None
    confirmation_url: str = ""
    payment_method_id: str = ""
    save_payment_method: bool = False
    paid_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
