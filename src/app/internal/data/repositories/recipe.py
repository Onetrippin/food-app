from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Avg, Count, F, Q
from django.utils import timezone
from decimal import Decimal

from app.internal.data.models import (
    AuthorApplicationModel,
    AuthorFollowModel,
    NotificationModel,
    RecipeFavoriteModel,
    RecipeIngredientModel,
    RecipeLikeModel,
    RecipeModel,
    RecipeReportModel,
    RecipeReviewModel,
)
from app.internal.domain.entities.author_follow import AuthorFollowEntity
from app.internal.domain.entities.notification import NotificationEntity
from app.internal.domain.entities.recipe import RecipeEntity
from app.internal.domain.entities.recipe_report import RecipeReportEntity
from app.internal.domain.entities.recipe_review import RecipeReviewEntity


class DjangoRecipeRepository:
    def list(self) -> list[RecipeEntity]:
        recipes = self._base_queryset().filter(is_published=True)
        return [self._build_entity(recipe) for recipe in recipes]

    def get_by_id(self, recipe_id: int) -> RecipeEntity | None:
        recipe = self._base_queryset().filter(id=recipe_id).first()

        if recipe is None:
            return None

        return self._build_entity(recipe)

    def search(self, query: str) -> list[RecipeEntity]:
        normalized_query = query.strip()

        if not normalized_query:
            return self.list()

        recipes = (
            self._base_queryset()
            .filter(
                is_published=True,
                Q(title__icontains=normalized_query)
                | Q(description__icontains=normalized_query)
            )
        )
        return [self._build_entity(recipe) for recipe in recipes]

    def find_by_ingredients(self, available_ingredients: list[str]) -> list[RecipeEntity]:
        normalized_available_ingredients = {
            ingredient.strip().lower()
            for ingredient in available_ingredients
            if ingredient.strip()
        }

        if not normalized_available_ingredients:
            return []

        recipes = self._base_queryset().filter(is_published=True)
        matched_recipes: list[RecipeEntity] = []

        for recipe in recipes:
            recipe_ingredient_names = [
                ingredient.name.strip().lower()
                for ingredient in recipe.ingredients.all()
                if ingredient.name.strip()
            ]

            if not recipe_ingredient_names:
                continue

            if all(
                ingredient_name in normalized_available_ingredients
                for ingredient_name in recipe_ingredient_names
            ):
                matched_recipes.append(self._build_entity(recipe))

        return matched_recipes

    @transaction.atomic
    def create(
        self,
        author_id: int,
        title: str,
        description: str,
        ingredients: list[str],
        price_amount: Decimal,
        price_currency: str,
        is_published: bool,
    ) -> RecipeEntity:
        recipe = RecipeModel.objects.create(
            author_id=author_id,
            title=title,
            description=description,
            price_amount=price_amount,
            price_currency=price_currency,
            is_published=is_published,
        )
        self._replace_ingredients(recipe=recipe, ingredients=ingredients)
        recipe = self._base_queryset().get(id=recipe.id)
        return self._build_entity(recipe)

    @transaction.atomic
    def update(
        self,
        recipe_id: int,
        title: str,
        description: str,
        ingredients: list[str],
        price_amount: Decimal,
        price_currency: str,
        is_published: bool,
    ) -> RecipeEntity | None:
        recipe = RecipeModel.objects.filter(id=recipe_id).first()

        if recipe is None:
            return None

        recipe.title = title
        recipe.description = description
        recipe.price_amount = price_amount
        recipe.price_currency = price_currency
        recipe.is_published = is_published
        recipe.save(
            update_fields=[
                "title",
                "description",
                "price_amount",
                "price_currency",
                "is_published",
                "updated_at",
            ]
        )
        self._replace_ingredients(recipe=recipe, ingredients=ingredients)
        recipe = self._base_queryset().get(id=recipe_id)
        return self._build_entity(recipe)

    def add_to_favorites(self, user_id: int, recipe_id: int) -> None:
        RecipeFavoriteModel.objects.get_or_create(user_id=user_id, recipe_id=recipe_id)

    def remove_from_favorites(self, user_id: int, recipe_id: int) -> None:
        RecipeFavoriteModel.objects.filter(user_id=user_id, recipe_id=recipe_id).delete()

    def list_favorites(self, user_id: int) -> list[RecipeEntity]:
        favorite_recipes = self._base_queryset().filter(
            favorited_by_users__user_id=user_id,
            is_published=True,
        )
        return [self._build_entity(recipe) for recipe in favorite_recipes]

    def add_like(self, user_id: int, recipe_id: int) -> None:
        RecipeLikeModel.objects.get_or_create(user_id=user_id, recipe_id=recipe_id)

    def remove_like(self, user_id: int, recipe_id: int) -> None:
        RecipeLikeModel.objects.filter(user_id=user_id, recipe_id=recipe_id).delete()

    def increment_views(self, recipe_id: int) -> None:
        RecipeModel.objects.filter(id=recipe_id).update(views_count=F("views_count") + 1)

    def delete(self, recipe_id: int) -> bool:
        deleted_count, _ = RecipeModel.objects.filter(id=recipe_id).delete()
        return deleted_count > 0

    def list_by_author(self, author_id: int) -> list[RecipeEntity]:
        recipes = self._base_queryset().filter(author_id=author_id)
        return [self._build_entity(recipe) for recipe in recipes]

    def list_reviews(self, recipe_id: int) -> list[RecipeReviewEntity]:
        reviews = RecipeReviewModel.objects.select_related("user").filter(recipe_id=recipe_id)
        return [
            RecipeReviewEntity(
                user_id=review.user_id,
                username=review.user.username,
                recipe_id=review.recipe_id,
                rating=review.rating,
                review_text=review.review_text,
                created_at=review.created_at,
                updated_at=review.updated_at,
            )
            for review in reviews
        ]

    def upsert_review(
        self,
        user_id: int,
        recipe_id: int,
        rating: int,
        review_text: str,
    ) -> RecipeReviewEntity:
        review, _ = RecipeReviewModel.objects.update_or_create(
            user_id=user_id,
            recipe_id=recipe_id,
            defaults={
                "rating": rating,
                "review_text": review_text,
            },
        )
        review = RecipeReviewModel.objects.select_related("user").get(id=review.id)
        return RecipeReviewEntity(
            user_id=review.user_id,
            username=review.user.username,
            recipe_id=review.recipe_id,
            rating=review.rating,
            review_text=review.review_text,
            created_at=review.created_at,
            updated_at=review.updated_at,
        )

    def create_report(
        self,
        user_id: int,
        recipe_id: int,
        reason: str,
        description: str,
    ) -> RecipeReportEntity:
        report = RecipeReportModel.objects.create(
            user_id=user_id,
            recipe_id=recipe_id,
            reason=reason,
            description=description,
        )
        return RecipeReportEntity(
            user_id=report.user_id,
            recipe_id=report.recipe_id,
            reason=report.reason,
            description=report.description,
            status=report.status,
            created_at=report.created_at,
            updated_at=report.updated_at,
        )

    def author_exists(self, author_id: int) -> bool:
        return (
            get_user_model()
            .objects.filter(id=author_id)
            .filter(
                Q(author_application__status=AuthorApplicationModel.Status.APPROVED)
                | Q(recipes__isnull=False)
            )
            .distinct()
            .exists()
        )

    def follow_author(self, subscriber_id: int, author_id: int) -> None:
        AuthorFollowModel.objects.get_or_create(
            subscriber_id=subscriber_id,
            author_id=author_id,
        )

    def unfollow_author(self, subscriber_id: int, author_id: int) -> None:
        AuthorFollowModel.objects.filter(
            subscriber_id=subscriber_id,
            author_id=author_id,
        ).delete()

    def list_followed_authors(self, subscriber_id: int) -> list[AuthorFollowEntity]:
        follows = AuthorFollowModel.objects.select_related("author").filter(
            subscriber_id=subscriber_id
        )
        return [
            AuthorFollowEntity(
                subscriber_id=follow.subscriber_id,
                author_id=follow.author_id,
                author_username=follow.author.username,
                created_at=follow.created_at,
            )
            for follow in follows
        ]

    def list_follower_ids(self, author_id: int) -> list[int]:
        return list(
            AuthorFollowModel.objects.filter(author_id=author_id).values_list(
                "subscriber_id",
                flat=True,
            )
        )

    def create_recipe_notifications(
        self,
        user_ids: list[int],
        recipe_id: int,
        recipe_title: str,
        author_username: str | None,
    ) -> None:
        normalized_user_ids = list(dict.fromkeys(user_id for user_id in user_ids if user_id > 0))

        if not normalized_user_ids:
            return

        display_author = author_username or "author"
        NotificationModel.objects.bulk_create(
            [
                NotificationModel(
                    user_id=user_id,
                    recipe_id=recipe_id,
                    notification_type=NotificationModel.NotificationType.RECIPE_PUBLISHED,
                    title="New recipe from author",
                    message=f"{display_author} published a new recipe: {recipe_title}",
                )
                for user_id in normalized_user_ids
            ]
        )

    def list_notifications(self, user_id: int) -> list[NotificationEntity]:
        notifications = NotificationModel.objects.filter(user_id=user_id)
        return [
            NotificationEntity(
                id=notification.id,
                user_id=notification.user_id,
                notification_type=notification.notification_type,
                title=notification.title,
                message=notification.message,
                recipe_id=notification.recipe_id,
                is_read=notification.is_read,
                created_at=notification.created_at,
                read_at=notification.read_at,
            )
            for notification in notifications
        ]

    def mark_notification_as_read(self, user_id: int, notification_id: int) -> bool:
        notification = NotificationModel.objects.filter(
            id=notification_id,
            user_id=user_id,
        ).first()

        if notification is None:
            return False

        if notification.is_read:
            return True

        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save(update_fields=["is_read", "read_at"])
        return True

    @staticmethod
    def _build_entity(recipe: RecipeModel) -> RecipeEntity:
        return RecipeEntity(
            id=recipe.id,
            title=recipe.title,
            description=recipe.description,
            ingredients=[ingredient.name for ingredient in recipe.ingredients.all()],
            author_id=recipe.author_id,
            author_username=recipe.author.username if recipe.author else None,
            price_amount=recipe.price_amount,
            price_currency=recipe.price_currency,
            is_published=recipe.is_published,
            views_count=recipe.views_count,
            likes_count=getattr(recipe, "likes_count", 0),
            favorites_count=getattr(recipe, "favorites_count", 0),
            average_rating=getattr(recipe, "average_rating", None),
            reviews_count=getattr(recipe, "reviews_count", 0),
            created_at=recipe.created_at,
            updated_at=recipe.updated_at,
        )

    @staticmethod
    def _replace_ingredients(recipe: RecipeModel, ingredients: list[str]) -> None:
        RecipeIngredientModel.objects.filter(recipe=recipe).delete()
        RecipeIngredientModel.objects.bulk_create(
            [
                RecipeIngredientModel(recipe=recipe, name=ingredient)
                for ingredient in ingredients
            ]
        )

    @staticmethod
    def _base_queryset():
        return (
            RecipeModel.objects.select_related("author")
            .prefetch_related("ingredients")
            .annotate(
                likes_count=Count("liked_by_users", distinct=True),
                favorites_count=Count("favorited_by_users", distinct=True),
                average_rating=Avg("reviews__rating"),
                reviews_count=Count("reviews", distinct=True),
            )
            .distinct()
        )
