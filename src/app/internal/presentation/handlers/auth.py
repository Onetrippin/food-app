from django.conf import settings
from django.core.mail import send_mail
from ninja.errors import HttpError
from ninja.security import HttpBearer

from app.internal.data.repositories.password_change_code import DjangoPasswordChangeCodeRepository
from app.internal.data.repositories.user import DjangoUserRepository
from app.internal.domain.entities.token import AccessTokenEntity, TokenPairEntity
from app.internal.domain.entities.user import UserEntity
from app.internal.domain.services.token import JWTTokenService
from app.internal.domain.services.user import UserService


def register_handler(username: str, email: str, password: str) -> TokenPairEntity:
    service = _build_user_service()

    try:
        return service.register(username=username, email=email, password=password)
    except ValueError as error:
        raise HttpError(400, str(error)) from error


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


def request_password_change_handler(user_id: int) -> dict[str, str]:
    service = _build_user_service()

    try:
        password_change_code = service.request_password_change(user_id=user_id)
    except ValueError as error:
        raise HttpError(400, str(error)) from error

    send_mail(
        subject="Password change code",
        message=(
            "Use this code to change your password: "
            f"{password_change_code.code}\n"
            f"The code expires at {password_change_code.expires_at.isoformat()}."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[password_change_code.email],
        fail_silently=False,
    )

    return {
        "detail": "Password change code sent to email.",
        "expires_at": password_change_code.expires_at.isoformat(),
    }


def confirm_password_change_handler(user_id: int, code: str, new_password: str) -> dict[str, str]:
    service = _build_user_service()

    try:
        service.confirm_password_change(user_id=user_id, code=code, new_password=new_password)
    except ValueError as error:
        raise HttpError(400, str(error)) from error

    return {"detail": "Password changed successfully."}


def delete_account_handler(user_id: int) -> dict[str, str]:
    service = _build_user_service()

    try:
        service.delete_account(user_id=user_id)
    except ValueError as error:
        raise HttpError(400, str(error)) from error

    return {"detail": "Account deleted successfully."}


class JWTBearerAuth(HttpBearer):
    def authenticate(self, request, token: str) -> UserEntity:
        return get_current_user_handler(access_token=token)


def _build_user_service() -> UserService:
    return UserService(
        user_repository=DjangoUserRepository(),
        password_change_code_repository=DjangoPasswordChangeCodeRepository(),
        token_service=JWTTokenService(),
    )
