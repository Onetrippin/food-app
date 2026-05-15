from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from app.internal.data.models import AuthorApplicationModel
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
            user = user_model.objects.select_related("author_application").get(id=user_id)
        except user_model.DoesNotExist:
            return None

        return self._build_entity(user)

    def exists_by_username(self, username: str) -> bool:
        user_model = get_user_model()
        return user_model.objects.filter(username=username).exists()

    def exists_by_email(self, email: str) -> bool:
        user_model = get_user_model()
        return user_model.objects.filter(email=email).exists()

    def create(self, username: str, email: str, password: str) -> UserEntity:
        user_model = get_user_model()
        user = user_model(username=username, email=email)
        self._validate_password(password=password, user=user)
        user.set_password(password)
        user.save()
        return self._build_entity(user)

    def validate_new_password(self, user_id: int, new_password: str) -> None:
        user_model = get_user_model()

        try:
            user = user_model.objects.get(id=user_id)
        except user_model.DoesNotExist:
            raise ValueError("User not found.")

        self._validate_password(password=new_password, user=user)

    def set_password(self, user_id: int, new_password: str) -> UserEntity | None:
        user_model = get_user_model()

        try:
            user = user_model.objects.get(id=user_id)
        except user_model.DoesNotExist:
            return None

        self._validate_password(password=new_password, user=user)
        user.set_password(new_password)
        user.save(update_fields=["password"])
        return self._build_entity(user)

    def delete(self, user_id: int) -> bool:
        user_model = get_user_model()
        deleted_count, _ = user_model.objects.filter(id=user_id).delete()
        return deleted_count > 0

    @staticmethod
    def _build_entity(user) -> UserEntity:
        author_application = DjangoUserRepository._get_author_application(user)
        author_application_status = author_application.status if author_application else None
        can_publish_recipes = bool(
            user.is_staff
            or author_application_status == "approved"
        )

        return UserEntity(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            is_staff=user.is_staff,
            can_publish_recipes=can_publish_recipes,
            author_application_status=author_application_status,
        )

    @staticmethod
    def _validate_password(password: str, user) -> None:
        try:
            validate_password(password, user=user)
        except DjangoValidationError as error:
            raise ValueError(" ".join(error.messages)) from error

    @staticmethod
    def _get_author_application(user) -> AuthorApplicationModel | None:
        try:
            return user.author_application
        except AuthorApplicationModel.DoesNotExist:
            return None
