from decimal import Decimal, InvalidOperation

from app.internal.domain.entities.author_follow import AuthorFollowEntity
from app.internal.domain.entities.notification import NotificationEntity
from app.internal.domain.entities.recipe_analytics import RecipeAnalyticsEntity
from app.internal.domain.entities.recipe import RecipeEntity
from app.internal.domain.entities.recipe_report import RecipeReportEntity
from app.internal.domain.entities.recipe_review import RecipeReviewEntity
from app.internal.domain.interfaces.payment import PaymentRepositoryInterface
from app.internal.domain.interfaces.recipe import RecipeRepositoryInterface


class RecipeService:
    def __init__(
        self,
        repository: RecipeRepositoryInterface,
        payment_repository: PaymentRepositoryInterface,
    ) -> None:
        self._repository = repository
        self._payment_repository = payment_repository

    def list_recipes(self) -> list[RecipeEntity]:
        return self._repository.list()

    def get_recipe(self, recipe_id: int) -> RecipeEntity:
        recipe = self._repository.get_by_id(recipe_id)

        if recipe is None:
            raise ValueError("Recipe not found.")

        return recipe

    def get_recipe_for_view(
        self,
        recipe_id: int,
        actor_id: int,
        actor_is_staff: bool,
    ) -> RecipeEntity:
        recipe = self.get_recipe(recipe_id=recipe_id)

        if not recipe.is_published and not actor_is_staff and recipe.author_id != actor_id:
            raise PermissionError("Recipe is not published.")

        if (
            recipe.price_amount > 0
            and not actor_is_staff
            and recipe.author_id != actor_id
            and not self._payment_repository.has_recipe_access(
                user_id=actor_id,
                recipe_id=recipe_id,
                author_id=recipe.author_id,
            )
        ):
            raise PermissionError("Recipe requires purchase or active author subscription.")

        self._repository.increment_views(recipe_id=recipe_id)
        refreshed_recipe = self._repository.get_by_id(recipe_id)

        if refreshed_recipe is None:
            raise ValueError("Recipe not found.")

        return refreshed_recipe

    def search_recipes(self, query: str) -> list[RecipeEntity]:
        return self._repository.search(query=query)

    def find_recipes_by_ingredients(self, available_ingredients: list[str]) -> list[RecipeEntity]:
        normalized_available_ingredients = [
            ingredient.strip()
            for ingredient in available_ingredients
            if ingredient.strip()
        ]

        if not normalized_available_ingredients:
            raise ValueError("At least one ingredient is required.")

        return self._repository.find_by_ingredients(
            available_ingredients=normalized_available_ingredients
        )

    def create_recipe(
        self,
        author_id: int,
        actor_is_staff: bool,
        actor_can_publish_recipes: bool,
        title: str,
        description: str,
        ingredients: list[str],
        price_amount: str,
        price_currency: str,
        is_published: bool,
    ) -> RecipeEntity:
        normalized_title = title.strip()

        if not normalized_title:
            raise ValueError("Title is required.")

        normalized_ingredients = self._normalize_ingredients(ingredients)
        normalized_price_amount = self._normalize_price_amount(price_amount)
        normalized_price_currency = self._normalize_currency(price_currency)
        self._validate_publish_permission(
            actor_is_staff=actor_is_staff,
            actor_can_publish_recipes=actor_can_publish_recipes,
            is_published=is_published,
        )
        recipe = self._repository.create(
            author_id=author_id,
            title=normalized_title,
            description=description.strip(),
            ingredients=normalized_ingredients,
            price_amount=normalized_price_amount,
            price_currency=normalized_price_currency,
            is_published=is_published,
        )
        self._notify_followers_about_publication(recipe=recipe)
        return recipe

    def update_recipe(
        self,
        actor_id: int,
        actor_is_staff: bool,
        actor_can_publish_recipes: bool,
        recipe_id: int,
        title: str,
        description: str,
        ingredients: list[str],
        price_amount: str,
        price_currency: str,
        is_published: bool,
    ) -> RecipeEntity:
        recipe = self.get_recipe(recipe_id=recipe_id)

        if not actor_is_staff and recipe.author_id != actor_id:
            raise PermissionError("You can edit only your own recipes.")

        normalized_title = title.strip()

        if not normalized_title:
            raise ValueError("Title is required.")

        normalized_ingredients = self._normalize_ingredients(ingredients)
        normalized_price_amount = self._normalize_price_amount(price_amount)
        normalized_price_currency = self._normalize_currency(price_currency)
        self._validate_publish_permission(
            actor_is_staff=actor_is_staff,
            actor_can_publish_recipes=actor_can_publish_recipes,
            is_published=is_published,
        )
        updated_recipe = self._repository.update(
            recipe_id=recipe_id,
            title=normalized_title,
            description=description.strip(),
            ingredients=normalized_ingredients,
            price_amount=normalized_price_amount,
            price_currency=normalized_price_currency,
            is_published=is_published,
        )

        if updated_recipe is None:
            raise ValueError("Recipe not found.")

        if not recipe.is_published and updated_recipe.is_published:
            self._notify_followers_about_publication(recipe=updated_recipe)

        return updated_recipe

    def add_recipe_to_favorites(self, user_id: int, recipe_id: int) -> None:
        self.get_recipe(recipe_id=recipe_id)
        self._repository.add_to_favorites(user_id=user_id, recipe_id=recipe_id)

    def remove_recipe_from_favorites(self, user_id: int, recipe_id: int) -> None:
        self.get_recipe(recipe_id=recipe_id)
        self._repository.remove_from_favorites(user_id=user_id, recipe_id=recipe_id)

    def list_favorite_recipes(self, user_id: int) -> list[RecipeEntity]:
        return self._repository.list_favorites(user_id=user_id)

    def add_recipe_like(self, user_id: int, recipe_id: int) -> None:
        recipe = self.get_recipe(recipe_id=recipe_id)

        if not recipe.is_published:
            raise ValueError("Recipe is not published.")

        self._repository.add_like(user_id=user_id, recipe_id=recipe_id)

    def remove_recipe_like(self, user_id: int, recipe_id: int) -> None:
        self.get_recipe(recipe_id=recipe_id)
        self._repository.remove_like(user_id=user_id, recipe_id=recipe_id)

    def delete_recipe(
        self,
        actor_id: int,
        actor_is_staff: bool,
        recipe_id: int,
    ) -> None:
        recipe = self.get_recipe(recipe_id=recipe_id)

        if not actor_is_staff and recipe.author_id != actor_id:
            raise PermissionError("You can delete only your own recipes.")

        deleted = self._repository.delete(recipe_id=recipe_id)

        if not deleted:
            raise ValueError("Recipe not found.")

    def get_author_analytics(self, author_id: int) -> RecipeAnalyticsEntity:
        recipes = self._repository.list_by_author(author_id=author_id)

        return RecipeAnalyticsEntity(
            total_recipes=len(recipes),
            published_recipes=sum(1 for recipe in recipes if recipe.is_published),
            total_views=sum(recipe.views_count for recipe in recipes),
            total_likes=sum(recipe.likes_count for recipe in recipes),
            total_favorites=sum(recipe.favorites_count for recipe in recipes),
            recipes=recipes,
        )

    def list_recipe_reviews(
        self,
        recipe_id: int,
        actor_id: int,
        actor_is_staff: bool,
    ) -> list[RecipeReviewEntity]:
        recipe = self.get_recipe(recipe_id=recipe_id)
        self._ensure_recipe_visible(
            recipe=recipe,
            actor_id=actor_id,
            actor_is_staff=actor_is_staff,
        )
        return self._repository.list_reviews(recipe_id=recipe_id)

    def add_recipe_review(
        self,
        user_id: int,
        actor_is_staff: bool,
        recipe_id: int,
        rating: int,
        review_text: str,
    ) -> RecipeReviewEntity:
        recipe = self.get_recipe(recipe_id=recipe_id)

        if recipe.author_id == user_id:
            raise PermissionError("You cannot review your own recipe.")

        if not recipe.is_published:
            raise PermissionError("Only published recipes can be reviewed.")

        if (
            recipe.price_amount > 0
            and not actor_is_staff
            and not self._payment_repository.has_recipe_access(
                user_id=user_id,
                recipe_id=recipe_id,
                author_id=recipe.author_id,
            )
        ):
            raise PermissionError("Recipe requires purchase or active author subscription.")

        normalized_rating = self._normalize_rating(rating)
        normalized_review_text = review_text.strip()
        return self._repository.upsert_review(
            user_id=user_id,
            recipe_id=recipe_id,
            rating=normalized_rating,
            review_text=normalized_review_text,
        )

    def report_recipe(
        self,
        user_id: int,
        recipe_id: int,
        reason: str,
        description: str,
    ) -> RecipeReportEntity:
        recipe = self.get_recipe(recipe_id=recipe_id)

        if recipe.author_id == user_id:
            raise PermissionError("You cannot report your own recipe.")

        if not recipe.is_published:
            raise PermissionError("Only published recipes can be reported.")

        normalized_reason = reason.strip()

        if not normalized_reason:
            raise ValueError("Report reason is required.")

        return self._repository.create_report(
            user_id=user_id,
            recipe_id=recipe_id,
            reason=normalized_reason,
            description=description.strip(),
        )

    def follow_author(self, subscriber_id: int, author_id: int) -> None:
        if subscriber_id == author_id:
            raise ValueError("You cannot follow yourself.")

        if not self._repository.author_exists(author_id=author_id):
            raise ValueError("Author not found.")

        self._repository.follow_author(
            subscriber_id=subscriber_id,
            author_id=author_id,
        )

    def unfollow_author(self, subscriber_id: int, author_id: int) -> None:
        if subscriber_id == author_id:
            raise ValueError("You cannot unfollow yourself.")

        if not self._repository.author_exists(author_id=author_id):
            raise ValueError("Author not found.")

        self._repository.unfollow_author(
            subscriber_id=subscriber_id,
            author_id=author_id,
        )

    def list_followed_authors(self, subscriber_id: int) -> list[AuthorFollowEntity]:
        return self._repository.list_followed_authors(subscriber_id=subscriber_id)

    def list_notifications(self, user_id: int) -> list[NotificationEntity]:
        return self._repository.list_notifications(user_id=user_id)

    def mark_notification_as_read(self, user_id: int, notification_id: int) -> None:
        marked = self._repository.mark_notification_as_read(
            user_id=user_id,
            notification_id=notification_id,
        )

        if not marked:
            raise ValueError("Notification not found.")

    @staticmethod
    def _validate_publish_permission(
        actor_is_staff: bool,
        actor_can_publish_recipes: bool,
        is_published: bool,
    ) -> None:
        if is_published and not actor_is_staff and not actor_can_publish_recipes:
            raise PermissionError("You do not have rights to publish recipes yet.")

    @staticmethod
    def _normalize_ingredients(ingredients: list[str]) -> list[str]:
        normalized_ingredients: list[str] = []
        seen_ingredients: set[str] = set()

        for ingredient in ingredients:
            normalized_ingredient = ingredient.strip()

            if not normalized_ingredient:
                continue

            normalized_key = normalized_ingredient.lower()

            if normalized_key in seen_ingredients:
                continue

            seen_ingredients.add(normalized_key)
            normalized_ingredients.append(normalized_ingredient)

        return normalized_ingredients

    @staticmethod
    def _normalize_price_amount(price_amount: str) -> Decimal:
        try:
            normalized_amount = Decimal(price_amount.strip())
        except (InvalidOperation, AttributeError) as error:
            raise ValueError("Invalid price amount.") from error

        if normalized_amount < 0:
            raise ValueError("Price amount cannot be negative.")

        return normalized_amount.quantize(Decimal("0.01"))

    @staticmethod
    def _normalize_currency(price_currency: str) -> str:
        normalized_currency = price_currency.strip().upper()

        if not normalized_currency:
            raise ValueError("Price currency is required.")

        return normalized_currency

    @staticmethod
    def _normalize_rating(rating: int) -> int:
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5.")

        return rating

    @staticmethod
    def _ensure_recipe_visible(
        recipe: RecipeEntity,
        actor_id: int,
        actor_is_staff: bool,
    ) -> None:
        if not recipe.is_published and not actor_is_staff and recipe.author_id != actor_id:
            raise PermissionError("Recipe is not published.")

    def _notify_followers_about_publication(self, recipe: RecipeEntity) -> None:
        if not recipe.is_published or recipe.id is None or recipe.author_id is None:
            return

        follower_ids = self._repository.list_follower_ids(author_id=recipe.author_id)
        self._repository.create_recipe_notifications(
            user_ids=follower_ids,
            recipe_id=recipe.id,
            recipe_title=recipe.title,
            author_username=recipe.author_username,
        )
