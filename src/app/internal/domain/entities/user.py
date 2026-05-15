from dataclasses import dataclass


@dataclass(slots=True, kw_only=True)
class UserEntity:
    id: int
    username: str
    email: str
    is_active: bool
    is_staff: bool
    can_publish_recipes: bool = False
    author_application_status: str | None = None
