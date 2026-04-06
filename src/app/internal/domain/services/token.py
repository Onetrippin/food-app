from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt
from django.conf import settings

from app.internal.domain.entities.token import AccessTokenEntity, TokenPairEntity
from app.internal.domain.entities.user import UserEntity


class JWTTokenService:
    def create_token_pair(self, user: UserEntity) -> TokenPairEntity:
        return TokenPairEntity(
            access_token=self._build_token(user=user, token_type="access", expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_LIFETIME_MINUTES)),
            refresh_token=self._build_token(user=user, token_type="refresh", expires_delta=timedelta(days=settings.JWT_REFRESH_TOKEN_LIFETIME_DAYS)),
        )

    def create_access_token(self, user: UserEntity) -> AccessTokenEntity:
        return AccessTokenEntity(
            access_token=self._build_token(user=user, token_type="access", expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_LIFETIME_MINUTES))
        )

    def get_access_subject(self, token: str) -> int:
        return self._decode_subject(token=token, expected_type="access")

    def get_refresh_subject(self, token: str) -> int:
        return self._decode_subject(token=token, expected_type="refresh")

    def _build_token(self, user: UserEntity, token_type: str, expires_delta: timedelta) -> str:
        now = datetime.now(tz=UTC)
        payload = {
            "sub": str(user.id),
            "type": token_type,
            "username": user.username,
            "iat": now,
            "exp": now + expires_delta,
        }

        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    def _decode_subject(self, token: str, expected_type: str) -> int:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except jwt.InvalidTokenError as error:
            raise ValueError("Invalid token.") from error

        token_type = payload.get("type")
        subject = payload.get("sub")

        if token_type != expected_type or subject is None:
            raise ValueError("Invalid token.")

        return int(subject)
