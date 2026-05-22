from __future__ import annotations

from decimal import Decimal

from django.utils import timezone

from app.internal.data.models import AuthorApplicationModel
from app.internal.domain.entities.author_application import AuthorApplicationEntity


class DjangoAuthorApplicationRepository:
    def submit(self, user_id: int, motivation: str) -> AuthorApplicationEntity:
        application, created = AuthorApplicationModel.objects.get_or_create(
            user_id=user_id,
            defaults={
                "motivation": motivation,
                "status": AuthorApplicationModel.Status.PENDING,
            },
        )

        if not created:
            if application.status == AuthorApplicationModel.Status.APPROVED:
                raise ValueError("You already have author publishing rights.")

            if application.status == AuthorApplicationModel.Status.PENDING:
                raise ValueError("Author application is already pending.")

            application.motivation = motivation
            application.status = AuthorApplicationModel.Status.PENDING
            application.review_comment = ""
            application.reviewed_at = None
            application.updated_at = timezone.now()
            application.save(
                update_fields=[
                    "motivation",
                    "status",
                    "review_comment",
                    "reviewed_at",
                    "updated_at",
                ]
            )

        return self._build_entity(application)

    def get_by_user_id(self, user_id: int) -> AuthorApplicationEntity | None:
        application = AuthorApplicationModel.objects.filter(user_id=user_id).first()

        if application is None:
            return None

        return self._build_entity(application)

    def update_subscription_settings(
        self,
        user_id: int,
        subscription_price: Decimal,
        subscription_currency: str,
        is_subscription_enabled: bool,
    ) -> AuthorApplicationEntity:
        application = AuthorApplicationModel.objects.filter(user_id=user_id).first()

        if application is None:
            raise ValueError("Author application not found.")

        if application.status != AuthorApplicationModel.Status.APPROVED:
            raise ValueError("Author application is not approved.")

        application.subscription_price = subscription_price
        application.subscription_currency = subscription_currency
        application.is_subscription_enabled = is_subscription_enabled
        application.updated_at = timezone.now()
        application.save(
            update_fields=[
                "subscription_price",
                "subscription_currency",
                "is_subscription_enabled",
                "updated_at",
            ]
        )

        return self._build_entity(application)

    @staticmethod
    def _build_entity(application: AuthorApplicationModel) -> AuthorApplicationEntity:
        return AuthorApplicationEntity(
            user_id=application.user_id,
            motivation=application.motivation,
            status=application.status,
            subscription_price=application.subscription_price,
            subscription_currency=application.subscription_currency,
            is_subscription_enabled=application.is_subscription_enabled,
            review_comment=application.review_comment,
            reviewed_at=application.reviewed_at,
            created_at=application.created_at,
            updated_at=application.updated_at,
        )
