from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, kw_only=True)
class PasswordChangeCodeEntity:
    user_id: int
    email: str
    code: str
    expires_at: datetime
