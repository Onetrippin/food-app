from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Protocol

from app.internal.domain.entities.author_subscription import AuthorSubscriptionEntity
from app.internal.domain.entities.payment import PaymentEntity
from app.internal.domain.entities.recipe_purchase import RecipePurchaseEntity


class PaymentRepositoryInterface(Protocol):
    def create_recipe_purchase_payment(
        self,
        user_id: int,
        recipe_id: int,
        amount: Decimal,
        currency: str,
        description: str,
        yookassa_payment_id: str,
        confirmation_url: str,
    ) -> PaymentEntity:
        ...

    def create_author_subscription_payment(
        self,
        user_id: int,
        author_id: int,
        amount: Decimal,
        currency: str,
        description: str,
        yookassa_payment_id: str,
        confirmation_url: str,
        save_payment_method: bool,
    ) -> PaymentEntity:
        ...

    def get_by_yookassa_payment_id(self, yookassa_payment_id: str) -> PaymentEntity | None:
        ...

    def mark_succeeded(
        self,
        yookassa_payment_id: str,
        payment_method_id: str = "",
        paid_at: datetime | None = None,
    ) -> PaymentEntity | None:
        ...

    def mark_canceled(self, yookassa_payment_id: str) -> PaymentEntity | None:
        ...

    def grant_recipe_purchase(self, yookassa_payment_id: str) -> None:
        ...

    def activate_author_subscription(
        self,
        yookassa_payment_id: str,
        duration_days: int,
        payment_method_id: str = "",
    ) -> None:
        ...

    def has_recipe_access(self, user_id: int, recipe_id: int, author_id: int | None) -> bool:
        ...

    def list_recipe_purchases(self, user_id: int) -> list[RecipePurchaseEntity]:
        ...

    def list_author_subscriptions(self, user_id: int) -> list[AuthorSubscriptionEntity]:
        ...
