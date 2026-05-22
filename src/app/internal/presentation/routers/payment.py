from ninja import Router, Schema

from app.internal.presentation.handlers.auth import JWTBearerAuth
from app.internal.presentation.handlers.payment import (
    create_author_subscription_checkout_handler,
    create_recipe_purchase_checkout_handler,
    handle_yookassa_webhook_handler,
    list_author_subscriptions_handler,
    list_recipe_purchases_handler,
)

router = Router(tags=["payments"])
jwt_bearer_auth = JWTBearerAuth()


class PaymentOutput(Schema):
    user_id: int
    payment_type: str
    status: str
    amount: str
    currency: str
    description: str
    yookassa_payment_id: str
    recipe_id: int | None
    author_id: int | None
    confirmation_url: str
    payment_method_id: str
    save_payment_method: bool
    paid_at: str | None
    created_at: str | None
    updated_at: str | None


class MessageOutput(Schema):
    detail: str


class RecipePurchaseOutput(Schema):
    user_id: int
    recipe_id: int
    purchased_at: str


class AuthorSubscriptionOutput(Schema):
    subscriber_id: int
    author_id: int
    amount: str
    currency: str
    payment_method_id: str
    started_at: str
    expires_at: str
    is_active: bool


@router.post("/recipes/{recipe_id}/checkout", auth=jwt_bearer_auth, response=PaymentOutput)
def create_recipe_purchase_checkout(request, recipe_id: int):
    return create_recipe_purchase_checkout_handler(user_id=request.auth.id, recipe_id=recipe_id)


@router.post("/authors/{author_id}/subscription/checkout", auth=jwt_bearer_auth, response=PaymentOutput)
def create_author_subscription_checkout(request, author_id: int):
    return create_author_subscription_checkout_handler(user_id=request.auth.id, author_id=author_id)


@router.get("/me/recipe-purchases", auth=jwt_bearer_auth, response=list[RecipePurchaseOutput])
def list_recipe_purchases(request):
    return list_recipe_purchases_handler(user_id=request.auth.id)


@router.get("/me/author-subscriptions", auth=jwt_bearer_auth, response=list[AuthorSubscriptionOutput])
def list_author_subscriptions(request):
    return list_author_subscriptions_handler(user_id=request.auth.id)


@router.post("/yookassa/webhook", response=MessageOutput)
def yookassa_webhook(request, payload: dict[str, object]):
    return handle_yookassa_webhook_handler(payload=payload)
