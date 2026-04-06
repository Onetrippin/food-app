from dataclasses import dataclass


@dataclass(slots=True, kw_only=True)
class TokenPairEntity:
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


@dataclass(slots=True, kw_only=True)
class AccessTokenEntity:
    access_token: str
    token_type: str = "Bearer"
