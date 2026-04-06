from ninja import Router, Schema

from app.internal.presentation.handlers.auth import JWTBearerAuth, login_handler, refresh_token_handler

router = Router(tags=["auth"])
jwt_bearer_auth = JWTBearerAuth()


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
