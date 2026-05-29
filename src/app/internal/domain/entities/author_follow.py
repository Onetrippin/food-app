from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, kw_only=True)
class AuthorFollowEntity:
    subscriber_id: int
    author_id: int
    author_username: str
    created_at: datetime
