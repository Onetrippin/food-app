from ninja.errors import HttpError
from ninja.security import HttpBearer

from app.internal.data.repositories.user import DjangoUserRepository
from app.internal.domain.entities.token import AccessTokenEntity, TokenPairEntity
from app.internal.domain.entities.user import UserEntity
from app.internal.domain.services.token import JWTTokenService
from app.internal.domain.services.user import UserService


def login_handler(username: str, password: str) -> TokenPairEntity:
    service = _build_user_service()

    try:
        return service.login(username=username, password=password)
    except ValueError as error:
        raise HttpError(401, str(error)) from error


def refresh_token_handler(refresh_token: str) -> AccessTokenEntity:
    service = _build_user_service()

    try:
        return service.refresh_access_token(refresh_token=refresh_token)
    except ValueError as error:
        raise HttpError(401, str(error)) from error


def get_current_user_handler(access_token: str) -> UserEntity:
    service = _build_user_service()

    try:
        return service.get_current_user(access_token=access_token)
    except ValueError as error:
        raise HttpError(401, str(error)) from error


class JWTBearerAuth(HttpBearer):
    def authenticate(self, request, token: str) -> UserEntity:
        return get_current_user_handler(access_token=token)


def _build_user_service() -> UserService:
    return UserService(
        user_repository=DjangoUserRepository(),
        token_service=JWTTokenService(),
    )
