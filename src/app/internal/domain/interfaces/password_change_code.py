from __future__ import annotations

from datetime import datetime
from typing import Protocol


class PasswordChangeCodeRepositoryInterface(Protocol):
    def invalidate_for_user(self, user_id: int) -> None:
        ...

    def create(self, user_id: int, code: str, expires_at: datetime) -> None:
        ...

    def consume(self, user_id: int, code: str) -> bool:
        ...
