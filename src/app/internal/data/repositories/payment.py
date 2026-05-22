from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from app.internal.data.models import (
    AuthorSubscriptionModel,
    PaymentModel,
    RecipePurchaseModel,
)
from app.internal.domain.entities.author_subscription import AuthorSubscriptionEntity
from app.internal.domain.entities.payment import PaymentEntity
from app.internal.domain.entities.recipe_purchase import RecipePurchaseEntity


class DjangoPaymentRepository:
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
        payment = PaymentModel.objects.create(
            user_id=user_id,
            recipe_id=recipe_id,
            payment_type=PaymentModel.PaymentType.RECIPE_PURCHASE,
            status=PaymentModel.PaymentStatus.PENDING,
            amount=amount,
            currency=currency,
            description=description,
            yookassa_payment_id=yookassa_payment_id,
            confirmation_url=confirmation_url,
        )
        return self._build_payment_entity(payment)

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
        payment = PaymentModel.objects.create(
            user_id=user_id,
            author_id=author_id,
            payment_type=PaymentModel.PaymentType.AUTHOR_SUBSCRIPTION,
            status=PaymentModel.PaymentStatus.PENDING,
            amount=amount,
            currency=currency,
            description=description,
            yookassa_payment_id=yookassa_payment_id,
            confirmation_url=confirmation_url,
            save_payment_method=save_payment_method,
        )
        return self._build_payment_entity(payment)

    def get_by_yookassa_payment_id(self, yookassa_payment_id: str) -> PaymentEntity | None:
        payment = PaymentModel.objects.filter(
            yookassa_payment_id=yookassa_payment_id
        ).first()

        if payment is None:
            return None

        return self._build_payment_entity(payment)

    def mark_succeeded(
        self,
        yookassa_payment_id: str,
        payment_method_id: str = "",
        paid_at: datetime | None = None,
    ) -> PaymentEntity | None:
        payment = PaymentModel.objects.filter(
            yookassa_payment_id=yookassa_payment_id
        ).first()

        if payment is None:
            return None

        payment.status = PaymentModel.PaymentStatus.SUCCEEDED
        payment.payment_method_id = payment_method_id
        payment.paid_at = paid_at or timezone.now()
        payment.save(update_fields=["status", "payment_method_id", "paid_at", "updated_at"])
        return self._build_payment_entity(payment)

    def mark_canceled(self, yookassa_payment_id: str) -> PaymentEntity | None:
        payment = PaymentModel.objects.filter(
            yookassa_payment_id=yookassa_payment_id
        ).first()

        if payment is None:
            return None

        payment.status = PaymentModel.PaymentStatus.CANCELED
        payment.save(update_fields=["status", "updated_at"])
        return self._build_payment_entity(payment)

    @transaction.atomic
    def grant_recipe_purchase(self, yookassa_payment_id: str) -> None:
        payment = PaymentModel.objects.select_for_update().get(
            yookassa_payment_id=yookassa_payment_id
        )

        if payment.recipe_id is None:
            return

        RecipePurchaseModel.objects.get_or_create(
            user_id=payment.user_id,
            recipe_id=payment.recipe_id,
            defaults={"payment": payment},
        )

    @transaction.atomic
    def activate_author_subscription(
        self,
        yookassa_payment_id: str,
        duration_days: int,
        payment_method_id: str = "",
    ) -> None:
        payment = PaymentModel.objects.select_for_update().get(
            yookassa_payment_id=yookassa_payment_id
        )

        if payment.author_id is None:
            return

        now = timezone.now()
        latest_subscription = (
            AuthorSubscriptionModel.objects.select_for_update()
            .filter(subscriber_id=payment.user_id, author_id=payment.author_id)
            .order_by("-expires_at")
            .first()
        )

        start_at = now
        if latest_subscription and latest_subscription.expires_at > now:
            start_at = latest_subscription.expires_at

        expires_at = start_at + timedelta(days=duration_days)

        if latest_subscription:
            latest_subscription.amount = payment.amount
            latest_subscription.currency = payment.currency
            latest_subscription.payment_method_id = (
                payment_method_id or latest_subscription.payment_method_id
            )
            latest_subscription.started_at = now
            latest_subscription.expires_at = expires_at
            latest_subscription.save(
                update_fields=[
                    "amount",
                    "currency",
                    "payment_method_id",
                    "started_at",
                    "expires_at",
                    "updated_at",
                ]
            )
            return

        AuthorSubscriptionModel.objects.create(
            subscriber_id=payment.user_id,
            author_id=payment.author_id,
            amount=payment.amount,
            currency=payment.currency,
            payment_method_id=payment_method_id,
            started_at=now,
            expires_at=expires_at,
        )

    def has_recipe_access(self, user_id: int, recipe_id: int, author_id: int | None) -> bool:
        direct_purchase_exists = RecipePurchaseModel.objects.filter(
            user_id=user_id,
            recipe_id=recipe_id,
        ).exists()

        if direct_purchase_exists:
            return True

        if author_id is None:
            return False

        return AuthorSubscriptionModel.objects.filter(
            subscriber_id=user_id,
            author_id=author_id,
            expires_at__gt=timezone.now(),
        ).exists()

    def list_recipe_purchases(self, user_id: int) -> list[RecipePurchaseEntity]:
        purchases = RecipePurchaseModel.objects.filter(user_id=user_id)
        return [
            RecipePurchaseEntity(
                user_id=purchase.user_id,
                recipe_id=purchase.recipe_id,
                purchased_at=purchase.purchased_at,
            )
            for purchase in purchases
        ]

    def list_author_subscriptions(self, user_id: int) -> list[AuthorSubscriptionEntity]:
        now = timezone.now()
        subscriptions = AuthorSubscriptionModel.objects.filter(subscriber_id=user_id)
        return [
            AuthorSubscriptionEntity(
                subscriber_id=subscription.subscriber_id,
                author_id=subscription.author_id,
                amount=subscription.amount,
                currency=subscription.currency,
                payment_method_id=subscription.payment_method_id,
                started_at=subscription.started_at,
                expires_at=subscription.expires_at,
                is_active=subscription.expires_at > now,
            )
            for subscription in subscriptions
        ]

    @staticmethod
    def _build_payment_entity(payment: PaymentModel) -> PaymentEntity:
        return PaymentEntity(
            user_id=payment.user_id,
            payment_type=payment.payment_type,
            status=payment.status,
            amount=payment.amount,
            currency=payment.currency,
            description=payment.description,
            yookassa_payment_id=payment.yookassa_payment_id,
            recipe_id=payment.recipe_id,
            author_id=payment.author_id,
            confirmation_url=payment.confirmation_url,
            payment_method_id=payment.payment_method_id,
            save_payment_method=payment.save_payment_method,
            paid_at=payment.paid_at,
            created_at=payment.created_at,
            updated_at=payment.updated_at,
        )
