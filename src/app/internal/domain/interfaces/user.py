from typing import Protocol

from app.internal.domain.entities.user import UserEntity


class UserRepositoryInterface(Protocol):
    def authenticate(self, username: str, password: str) -> UserEntity | None:
        ...

    def get_by_id(self, user_id: int) -> UserEntity | None:
        ...

    def exists_by_username(self, username: str) -> bool:
        ...

    def exists_by_email(self, email: str) -> bool:
        ...

    def create(self, username: str, email: str, password: str) -> UserEntity:
        ...

    def validate_new_password(self, user_id: int, new_password: str) -> None:
        ...

    def set_password(self, user_id: int, new_password: str) -> UserEntity | None:
        ...

    def delete(self, user_id: int) -> bool:
        ...
