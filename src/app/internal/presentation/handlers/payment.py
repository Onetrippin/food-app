from ninja.errors import HttpError

from app.internal.data.repositories.author_application import DjangoAuthorApplicationRepository
from app.internal.data.repositories.payment import DjangoPaymentRepository
from app.internal.data.repositories.recipe import DjangoRecipeRepository
from app.internal.data.repositories.yookassa import YooKassaProvider
from app.internal.domain.services.payment import PaymentService


def create_recipe_purchase_checkout_handler(user_id: int, recipe_id: int) -> dict[str, object]:
    service = _build_payment_service()

    try:
        payment = service.create_recipe_purchase_checkout(user_id=user_id, recipe_id=recipe_id)
    except ValueError as error:
        message = str(error)
        if message == "Recipe not found.":
            status_code = 404
        elif "YooKassa" in message:
            status_code = 502
        else:
            status_code = 400
        raise HttpError(status_code, message) from error

    return _serialize_payment(payment)


def create_author_subscription_checkout_handler(user_id: int, author_id: int) -> dict[str, object]:
    service = _build_payment_service()

    try:
        payment = service.create_author_subscription_checkout(user_id=user_id, author_id=author_id)
    except ValueError as error:
        message = str(error)
        status_code = 502 if "YooKassa" in message else 400
        raise HttpError(status_code, message) from error

    return _serialize_payment(payment)


def handle_yookassa_webhook_handler(payload: dict[str, object]) -> dict[str, str]:
    service = _build_payment_service()

    try:
        service.handle_yookassa_webhook(payload=payload)
    except ValueError as error:
        raise HttpError(400, str(error)) from error

    return {"detail": "Webhook processed."}


def list_recipe_purchases_handler(user_id: int) -> list[dict[str, object]]:
    service = _build_payment_service()
    purchases = service.list_recipe_purchases(user_id=user_id)
    return [
        {
            "user_id": purchase.user_id,
            "recipe_id": purchase.recipe_id,
            "purchased_at": purchase.purchased_at.isoformat(),
        }
        for purchase in purchases
    ]


def list_author_subscriptions_handler(user_id: int) -> list[dict[str, object]]:
    service = _build_payment_service()
    subscriptions = service.list_author_subscriptions(user_id=user_id)
    return [
        {
            "subscriber_id": subscription.subscriber_id,
            "author_id": subscription.author_id,
            "amount": f"{subscription.amount:.2f}",
            "currency": subscription.currency,
            "payment_method_id": subscription.payment_method_id,
            "started_at": subscription.started_at.isoformat(),
            "expires_at": subscription.expires_at.isoformat(),
            "is_active": subscription.is_active,
        }
        for subscription in subscriptions
    ]


def _serialize_payment(payment) -> dict[str, object]:
    return {
        "user_id": payment.user_id,
        "payment_type": payment.payment_type,
        "status": payment.status,
        "amount": f"{payment.amount:.2f}",
        "currency": payment.currency,
        "description": payment.description,
        "yookassa_payment_id": payment.yookassa_payment_id,
        "recipe_id": payment.recipe_id,
        "author_id": payment.author_id,
        "confirmation_url": payment.confirmation_url,
        "payment_method_id": payment.payment_method_id,
        "save_payment_method": payment.save_payment_method,
        "paid_at": payment.paid_at.isoformat() if payment.paid_at else None,
        "created_at": payment.created_at.isoformat() if payment.created_at else None,
        "updated_at": payment.updated_at.isoformat() if payment.updated_at else None,
    }


def _build_payment_service() -> PaymentService:
    return PaymentService(
        payment_repository=DjangoPaymentRepository(),
        recipe_repository=DjangoRecipeRepository(),
        author_application_repository=DjangoAuthorApplicationRepository(),
        yookassa_provider=YooKassaProvider(),
    )
