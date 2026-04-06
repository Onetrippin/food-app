from typing import Protocol

from app.internal.domain.entities.user import UserEntity


class UserRepositoryInterface(Protocol):
    def authenticate(self, username: str, password: str) -> UserEntity | None:
        ...

    def get_by_id(self, user_id: int) -> UserEntity | None:
        ...
