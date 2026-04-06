from django.contrib.auth import authenticate, get_user_model

from app.internal.domain.entities.user import UserEntity


class DjangoUserRepository:
    def authenticate(self, username: str, password: str) -> UserEntity | None:
        user = authenticate(username=username, password=password)

        if user is None:
            return None

        return self._build_entity(user)

    def get_by_id(self, user_id: int) -> UserEntity | None:
        user_model = get_user_model()

        try:
            user = user_model.objects.get(id=user_id)
        except user_model.DoesNotExist:
            return None

        return self._build_entity(user)

    @staticmethod
    def _build_entity(user) -> UserEntity:
        return UserEntity(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            is_staff=user.is_staff,
        )
