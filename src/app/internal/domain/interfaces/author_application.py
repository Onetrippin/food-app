from typing import Protocol

from app.internal.domain.entities.author_application import AuthorApplicationEntity


class AuthorApplicationRepositoryInterface(Protocol):
    def submit(self, user_id: int, motivation: str) -> AuthorApplicationEntity:
        ...

    def get_by_user_id(self, user_id: int) -> AuthorApplicationEntity | None:
        ...
