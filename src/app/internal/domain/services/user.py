from app.internal.domain.entities.token import AccessTokenEntity, TokenPairEntity
from app.internal.domain.entities.user import UserEntity
from app.internal.domain.interfaces.token import TokenServiceInterface
from app.internal.domain.interfaces.user import UserRepositoryInterface


class UserService:
    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        token_service: TokenServiceInterface,
    ) -> None:
        self._user_repository = user_repository
        self._token_service = token_service

    def login(self, username: str, password: str) -> TokenPairEntity:
        user = self._user_repository.authenticate(username=username, password=password)

        if user is None or not user.is_active:
            raise ValueError("Invalid credentials.")

        return self._token_service.create_token_pair(user)

    def refresh_access_token(self, refresh_token: str) -> AccessTokenEntity:
        user_id = self._token_service.get_refresh_subject(refresh_token)
        user = self._user_repository.get_by_id(user_id)

        if user is None or not user.is_active:
            raise ValueError("Invalid token.")

        return self._token_service.create_access_token(user)

    def get_current_user(self, access_token: str) -> UserEntity:
        user_id = self._token_service.get_access_subject(access_token)
        user = self._user_repository.get_by_id(user_id)

        if user is None or not user.is_active:
            raise ValueError("Invalid token.")

        return user
