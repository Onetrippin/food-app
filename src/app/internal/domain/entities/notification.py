from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, kw_only=True)
class NotificationEntity:
    id: int
    user_id: int
    notification_type: str
    title: str
    message: str
    recipe_id: int | None
    is_read: bool
    created_at: datetime
    read_at: datetime | None = None
