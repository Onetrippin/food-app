from ninja import Router, Schema

from app.internal.presentation.handlers.auth import (
    JWTBearerAuth,
    confirm_password_change_handler,
    delete_account_handler,
    login_handler,
    refresh_token_handler,
    register_handler,
    request_password_change_handler,
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


class PasswordChangeConfirmInput(Schema):
    code: str
    new_password: str


class MessageOutput(Schema):
    detail: str


class PasswordChangeRequestOutput(Schema):
    detail: str
    expires_at: str


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
