from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from django.conf import settings

from app.internal.domain.entities.author_application import AuthorApplicationEntity
from app.internal.domain.entities.password_change_code import PasswordChangeCodeEntity
from app.internal.domain.entities.token import AccessTokenEntity, TokenPairEntity
from app.internal.domain.entities.user import UserEntity
from app.internal.domain.interfaces.author_application import AuthorApplicationRepositoryInterface
from app.internal.domain.interfaces.password_change_code import PasswordChangeCodeRepositoryInterface
from app.internal.domain.interfaces.token import TokenServiceInterface
from app.internal.domain.interfaces.user import UserRepositoryInterface


class UserService:
    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        author_application_repository: AuthorApplicationRepositoryInterface,
        password_change_code_repository: PasswordChangeCodeRepositoryInterface,
        token_service: TokenServiceInterface,
    ) -> None:
        self._user_repository = user_repository
        self._author_application_repository = author_application_repository
        self._password_change_code_repository = password_change_code_repository
        self._token_service = token_service

    def register(self, username: str, email: str, password: str) -> TokenPairEntity:
        normalized_email = email.strip().lower()
        normalized_username = username.strip()

        if not normalized_username:
            raise ValueError("Username is required.")

        if not normalized_email:
            raise ValueError("Email is required.")

        if self._user_repository.exists_by_username(normalized_username):
            raise ValueError("Username is already taken.")

        if self._user_repository.exists_by_email(normalized_email):
            raise ValueError("Email is already taken.")

        user = self._user_repository.create(
            username=normalized_username,
            email=normalized_email,
            password=password,
        )

        return self._token_service.create_token_pair(user)

    def login(self, username: str, password: str) -> TokenPairEntity:
        user = self._user_repository.authenticate(username=username, password=password)

        if user is None or not user.is_active:
            raise ValueError("Invalid credentials.")

        return self._token_service.create_token_pair(user)

    def refresh_access_token(self, refresh_token: str) -> AccessTokenEntity:
        user_id = self._token_service.get_refresh_subject(refresh_token)
        user = self._user_repository.get_by_id(user_id)

        if user is None or not user.is_active:
            raise ValueError("Invalid token.")

        return self._token_service.create_access_token(user)

    def get_current_user(self, access_token: str) -> UserEntity:
        user_id = self._token_service.get_access_subject(access_token)
        user = self._user_repository.get_by_id(user_id)

        if user is None or not user.is_active:
            raise ValueError("Invalid token.")

        return user

    def request_password_change(self, user_id: int) -> PasswordChangeCodeEntity:
        user = self._user_repository.get_by_id(user_id)

        if user is None or not user.is_active:
            raise ValueError("User not found.")

        if not user.email:
            raise ValueError("Email is required to change password.")

        code = f"{secrets.randbelow(1_000_000):06d}"
        expires_at = datetime.now(tz=UTC) + timedelta(
            minutes=settings.PASSWORD_CHANGE_CODE_TTL_MINUTES
        )

        self._password_change_code_repository.invalidate_for_user(user_id)
        self._password_change_code_repository.create(
            user_id=user_id,
            code=code,
            expires_at=expires_at,
        )

        return PasswordChangeCodeEntity(
            user_id=user.id,
            email=user.email,
            code=code,
            expires_at=expires_at,
        )

    def confirm_password_change(
        self,
        user_id: int,
        code: str,
        new_password: str,
    ) -> None:
        user = self._user_repository.get_by_id(user_id)

        if user is None or not user.is_active:
            raise ValueError("User not found.")

        self._user_repository.validate_new_password(
            user_id=user_id,
            new_password=new_password,
        )

        if not self._password_change_code_repository.consume(user_id=user_id, code=code):
            raise ValueError("Invalid or expired code.")

        updated_user = self._user_repository.set_password(
            user_id=user_id,
            new_password=new_password,
        )

        if updated_user is None:
            raise ValueError("User not found.")

    def delete_account(self, user_id: int) -> None:
        deleted = self._user_repository.delete(user_id)

        if not deleted:
            raise ValueError("User not found.")

    def submit_author_application(self, user_id: int, motivation: str) -> AuthorApplicationEntity:
        user = self._user_repository.get_by_id(user_id)

        if user is None or not user.is_active:
            raise ValueError("User not found.")

        normalized_motivation = motivation.strip()

        if not normalized_motivation:
            raise ValueError("Motivation is required.")

        return self._author_application_repository.submit(
            user_id=user_id,
            motivation=normalized_motivation,
        )

    def get_author_application(self, user_id: int) -> AuthorApplicationEntity | None:
        user = self._user_repository.get_by_id(user_id)

        if user is None or not user.is_active:
            raise ValueError("User not found.")

        return self._author_application_repository.get_by_user_id(user_id=user_id)

    def update_author_profile(
        self,
        user_id: int,
        subscription_price: Decimal,
        subscription_currency: str,
        is_subscription_enabled: bool,
    ) -> AuthorApplicationEntity:
        user = self._user_repository.get_by_id(user_id)

        if user is None or not user.is_active:
            raise ValueError("User not found.")

        if subscription_price < 0:
            raise ValueError("Subscription price cannot be negative.")

        normalized_currency = subscription_currency.strip().upper()
        if not normalized_currency:
            raise ValueError("Subscription currency is required.")

        return self._author_application_repository.update_subscription_settings(
            user_id=user_id,
            subscription_price=subscription_price,
            subscription_currency=normalized_currency,
            is_subscription_enabled=is_subscription_enabled,
        )
