from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from django.conf import settings

from app.internal.domain.entities.author_application import AuthorApplicationEntity
from app.internal.domain.entities.author_subscription import AuthorSubscriptionEntity
from app.internal.domain.entities.payment import PaymentEntity
from app.internal.domain.entities.recipe_purchase import RecipePurchaseEntity
from app.internal.domain.interfaces.author_application import AuthorApplicationRepositoryInterface
from app.internal.domain.interfaces.payment import PaymentRepositoryInterface
from app.internal.domain.interfaces.recipe import RecipeRepositoryInterface
from app.internal.domain.interfaces.yookassa import YooKassaProviderInterface


class PaymentService:
    def __init__(
        self,
        payment_repository: PaymentRepositoryInterface,
        recipe_repository: RecipeRepositoryInterface,
        author_application_repository: AuthorApplicationRepositoryInterface,
        yookassa_provider: YooKassaProviderInterface,
    ) -> None:
        self._payment_repository = payment_repository
        self._recipe_repository = recipe_repository
        self._author_application_repository = author_application_repository
        self._yookassa_provider = yookassa_provider

    def create_recipe_purchase_checkout(self, user_id: int, recipe_id: int) -> PaymentEntity:
        recipe = self._recipe_repository.get_by_id(recipe_id)

        if recipe is None:
            raise ValueError("Recipe not found.")

        if not recipe.is_published:
            raise ValueError("Recipe is not published.")

        if recipe.author_id == user_id:
            raise ValueError("You already own this recipe as its author.")

        if recipe.price_amount <= 0:
            raise ValueError("This recipe is free and does not require payment.")

        if self._payment_repository.has_recipe_access(
            user_id=user_id,
            recipe_id=recipe_id,
            author_id=recipe.author_id,
        ):
            raise ValueError("You already have access to this recipe.")

        description = f"Purchase recipe #{recipe.id}: {recipe.title}"
        yookassa_payment = self._yookassa_provider.create_payment(
            amount_value=f"{recipe.price_amount:.2f}",
            currency=recipe.price_currency,
            description=description,
            return_url=settings.YOOKASSA_RETURN_URL,
            metadata={
                "payment_type": "recipe_purchase",
                "recipe_id": str(recipe_id),
                "user_id": str(user_id),
            },
        )

        return self._payment_repository.create_recipe_purchase_payment(
            user_id=user_id,
            recipe_id=recipe_id,
            amount=recipe.price_amount,
            currency=recipe.price_currency,
            description=description,
            yookassa_payment_id=str(yookassa_payment["id"]),
            confirmation_url=str(
                yookassa_payment.get("confirmation", {}).get("confirmation_url", "")
            ),
        )

    def create_author_subscription_checkout(self, user_id: int, author_id: int) -> PaymentEntity:
        if user_id == author_id:
            raise ValueError("You cannot subscribe to yourself.")

        author_application = self._author_application_repository.get_by_user_id(author_id)

        if author_application is None or author_application.status != "approved":
            raise ValueError("Author subscriptions are unavailable for this author.")

        if not author_application.is_subscription_enabled:
            raise ValueError("Author subscription is disabled.")

        if author_application.subscription_price <= 0:
            raise ValueError("Author subscription price must be greater than zero.")

        description = f"Subscribe to author #{author_id}"
        yookassa_payment = self._yookassa_provider.create_payment(
            amount_value=f"{author_application.subscription_price:.2f}",
            currency=author_application.subscription_currency,
            description=description,
            return_url=settings.YOOKASSA_RETURN_URL,
            metadata={
                "payment_type": "author_subscription",
                "author_id": str(author_id),
                "user_id": str(user_id),
            },
            save_payment_method=True,
        )

        return self._payment_repository.create_author_subscription_payment(
            user_id=user_id,
            author_id=author_id,
            amount=author_application.subscription_price,
            currency=author_application.subscription_currency,
            description=description,
            yookassa_payment_id=str(yookassa_payment["id"]),
            confirmation_url=str(
                yookassa_payment.get("confirmation", {}).get("confirmation_url", "")
            ),
            save_payment_method=True,
        )

    def handle_yookassa_webhook(self, payload: dict[str, object]) -> None:
        event = str(payload.get("event", ""))
        payment_object = payload.get("object")

        if not isinstance(payment_object, dict):
            raise ValueError("Invalid YooKassa payload.")

        yookassa_payment_id = str(payment_object.get("id", ""))

        if not yookassa_payment_id:
            raise ValueError("Missing YooKassa payment id.")

        if event == "payment.succeeded":
            payment_method = payment_object.get("payment_method")
            payment_method_id = ""

            if isinstance(payment_method, dict):
                payment_method_id = str(payment_method.get("id", ""))

            paid_at = None
            paid_at_raw = payment_object.get("captured_at") or payment_object.get("created_at")
            if isinstance(paid_at_raw, str):
                paid_at = self._parse_yookassa_datetime(paid_at_raw)

            payment = self._payment_repository.mark_succeeded(
                yookassa_payment_id=yookassa_payment_id,
                payment_method_id=payment_method_id,
                paid_at=paid_at,
            )

            if payment is None:
                raise ValueError("Payment not found.")

            if payment.payment_type == "recipe_purchase":
                self._payment_repository.grant_recipe_purchase(
                    yookassa_payment_id=yookassa_payment_id
                )
                return

            if payment.payment_type == "author_subscription":
                self._payment_repository.activate_author_subscription(
                    yookassa_payment_id=yookassa_payment_id,
                    duration_days=settings.AUTHOR_SUBSCRIPTION_DURATION_DAYS,
                    payment_method_id=payment_method_id,
                )
                return

        if event == "payment.canceled":
            payment = self._payment_repository.mark_canceled(
                yookassa_payment_id=yookassa_payment_id
            )

            if payment is None:
                raise ValueError("Payment not found.")

            return

    def list_recipe_purchases(self, user_id: int) -> list[RecipePurchaseEntity]:
        return self._payment_repository.list_recipe_purchases(user_id=user_id)

    def list_author_subscriptions(self, user_id: int) -> list[AuthorSubscriptionEntity]:
        return self._payment_repository.list_author_subscriptions(user_id=user_id)

    @staticmethod
    def _parse_yookassa_datetime(value: str) -> datetime:
        normalized_value = value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized_value).astimezone(UTC)
