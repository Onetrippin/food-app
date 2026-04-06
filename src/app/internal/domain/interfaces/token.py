from typing import Protocol

from app.internal.domain.entities.token import AccessTokenEntity, TokenPairEntity
from app.internal.domain.entities.user import UserEntity


class TokenServiceInterface(Protocol):
    def create_token_pair(self, user: UserEntity) -> TokenPairEntity:
        ...

    def create_access_token(self, user: UserEntity) -> AccessTokenEntity:
        ...

    def get_access_subject(self, token: str) -> int:
        ...

    def get_refresh_subject(self, token: str) -> int:
        ...
