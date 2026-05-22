from ninja import Router, Schema

from app.internal.presentation.handlers.auth import (
    JWTBearerAuth,
    confirm_password_change_handler,
    delete_account_handler,
    get_author_application_handler,
    login_handler,
    refresh_token_handler,
    register_handler,
    submit_author_application_handler,
    request_password_change_handler,
    update_author_profile_handler,
)

router = Router(tags=["auth"])
jwt_bearer_auth = JWTBearerAuth()


class RegisterInput(Schema):
    username: str
    email: str
    password: str


class LoginInput(Schema):
    username: str
    password: str


class RefreshTokenInput(Schema):
    refresh_token: str


class TokenPairOutput(Schema):
    access_token: str
    refresh_token: str
    token_type: str


class AccessTokenOutput(Schema):
    access_token: str
    token_type: str


class CurrentUserOutput(Schema):
    id: int
    username: str
    email: str
    is_active: bool
    is_staff: bool
    can_publish_recipes: bool
    author_application_status: str | None


class PasswordChangeConfirmInput(Schema):
    code: str
    new_password: str


class MessageOutput(Schema):
    detail: str


class PasswordChangeRequestOutput(Schema):
    detail: str
    expires_at: str


class AuthorApplicationInput(Schema):
    motivation: str


class AuthorApplicationOutput(Schema):
    user_id: int
    motivation: str
    status: str
    subscription_price: str
    subscription_currency: str
    is_subscription_enabled: bool
    review_comment: str
    reviewed_at: str | None
    created_at: str | None
    updated_at: str | None


class AuthorApplicationStatusOutput(Schema):
    application: AuthorApplicationOutput | None


class AuthorProfileInput(Schema):
    subscription_price: str
    subscription_currency: str = "RUB"
    is_subscription_enabled: bool


@router.post("/register", response=TokenPairOutput)
def register(request, payload: RegisterInput):
    token_pair = register_handler(
        username=payload.username,
        email=payload.email,
        password=payload.password,
    )
    return {
        "access_token": token_pair.access_token,
        "refresh_token": token_pair.refresh_token,
        "token_type": token_pair.token_type,
    }


@router.post("/login", response=TokenPairOutput)
def login(request, payload: LoginInput):
    token_pair = login_handler(username=payload.username, password=payload.password)
    return {
        "access_token": token_pair.access_token,
        "refresh_token": token_pair.refresh_token,
        "token_type": token_pair.token_type,
    }


@router.post("/refresh", response=AccessTokenOutput)
def refresh_access_token(request, payload: RefreshTokenInput):
    access_token = refresh_token_handler(refresh_token=payload.refresh_token)
    return {
        "access_token": access_token.access_token,
        "token_type": access_token.token_type,
    }


@router.get("/me", auth=jwt_bearer_auth, response=CurrentUserOutput)
def me(request):
    user = request.auth
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "is_staff": user.is_staff,
        "can_publish_recipes": user.can_publish_recipes,
        "author_application_status": user.author_application_status,
    }


@router.post("/password/change/request", auth=jwt_bearer_auth, response=PasswordChangeRequestOutput)
def request_password_change(request):
    return request_password_change_handler(user_id=request.auth.id)


@router.post("/password/change/confirm", auth=jwt_bearer_auth, response=MessageOutput)
def confirm_password_change(request, payload: PasswordChangeConfirmInput):
    return confirm_password_change_handler(
        user_id=request.auth.id,
        code=payload.code,
        new_password=payload.new_password,
    )


@router.delete("/account", auth=jwt_bearer_auth, response=MessageOutput)
def delete_account(request):
    return delete_account_handler(user_id=request.auth.id)


@router.post("/author-application", auth=jwt_bearer_auth, response=AuthorApplicationOutput)
def submit_author_application(request, payload: AuthorApplicationInput):
    application = submit_author_application_handler(
        user_id=request.auth.id,
        motivation=payload.motivation,
    )
    return {
        "user_id": application.user_id,
        "motivation": application.motivation,
        "status": application.status,
        "subscription_price": f"{application.subscription_price:.2f}",
        "subscription_currency": application.subscription_currency,
        "is_subscription_enabled": application.is_subscription_enabled,
        "review_comment": application.review_comment,
        "reviewed_at": application.reviewed_at.isoformat() if application.reviewed_at else None,
        "created_at": application.created_at.isoformat() if application.created_at else None,
        "updated_at": application.updated_at.isoformat() if application.updated_at else None,
    }


@router.get("/author-application", auth=jwt_bearer_auth, response=AuthorApplicationStatusOutput)
def get_author_application(request):
    application = get_author_application_handler(user_id=request.auth.id)

    if application is None:
        return {"application": None}

    return {
        "application": {
            "user_id": application.user_id,
            "motivation": application.motivation,
            "status": application.status,
            "subscription_price": f"{application.subscription_price:.2f}",
            "subscription_currency": application.subscription_currency,
            "is_subscription_enabled": application.is_subscription_enabled,
            "review_comment": application.review_comment,
            "reviewed_at": application.reviewed_at.isoformat() if application.reviewed_at else None,
            "created_at": application.created_at.isoformat() if application.created_at else None,
            "updated_at": application.updated_at.isoformat() if application.updated_at else None,
        }
    }


@router.put("/author-profile", auth=jwt_bearer_auth, response=AuthorApplicationOutput)
def update_author_profile(request, payload: AuthorProfileInput):
    application = update_author_profile_handler(
        user_id=request.auth.id,
        subscription_price=payload.subscription_price,
        subscription_currency=payload.subscription_currency,
        is_subscription_enabled=payload.is_subscription_enabled,
    )
    return {
        "user_id": application.user_id,
        "motivation": application.motivation,
        "status": application.status,
        "subscription_price": f"{application.subscription_price:.2f}",
        "subscription_currency": application.subscription_currency,
        "is_subscription_enabled": application.is_subscription_enabled,
        "review_comment": application.review_comment,
        "reviewed_at": application.reviewed_at.isoformat() if application.reviewed_at else None,
        "created_at": application.created_at.isoformat() if application.created_at else None,
        "updated_at": application.updated_at.isoformat() if application.updated_at else None,
    }
