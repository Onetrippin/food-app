from __future__ import annotations

from decimal import Decimal
from typing import Protocol

from app.internal.domain.entities.author_follow import AuthorFollowEntity
from app.internal.domain.entities.notification import NotificationEntity
from app.internal.domain.entities.recipe import RecipeEntity
from app.internal.domain.entities.recipe_report import RecipeReportEntity
from app.internal.domain.entities.recipe_review import RecipeReviewEntity


class RecipeRepositoryInterface(Protocol):
    def list(self) -> list[RecipeEntity]:
        ...

    def get_by_id(self, recipe_id: int) -> RecipeEntity | None:
        ...

    def search(self, query: str) -> list[RecipeEntity]:
        ...

    def find_by_ingredients(self, available_ingredients: list[str]) -> list[RecipeEntity]:
        ...

    def create(
        self,
        author_id: int,
        title: str,
        description: str,
        ingredients: list[str],
        price_amount: Decimal,
        price_currency: str,
        is_published: bool,
        moderation_status: str,
        moderation_comment: str,
    ) -> RecipeEntity:
        ...

    def update(
        self,
        recipe_id: int,
        title: str,
        description: str,
        ingredients: list[str],
        price_amount: Decimal,
        price_currency: str,
        is_published: bool,
        moderation_status: str,
        moderation_comment: str,
    ) -> RecipeEntity | None:
        ...

    def add_to_favorites(self, user_id: int, recipe_id: int) -> None:
        ...

    def remove_from_favorites(self, user_id: int, recipe_id: int) -> None:
        ...

    def list_favorites(self, user_id: int) -> list[RecipeEntity]:
        ...

    def add_like(self, user_id: int, recipe_id: int) -> None:
        ...

    def remove_like(self, user_id: int, recipe_id: int) -> None:
        ...

    def increment_views(self, recipe_id: int) -> None:
        ...

    def delete(self, recipe_id: int) -> bool:
        ...

    def list_by_author(self, author_id: int) -> list[RecipeEntity]:
        ...

    def list_reviews(self, recipe_id: int) -> list[RecipeReviewEntity]:
        ...

    def upsert_review(
        self,
        user_id: int,
        recipe_id: int,
        rating: int,
        review_text: str,
        moderation_status: str,
    ) -> RecipeReviewEntity:
        ...

    def create_report(
        self,
        user_id: int,
        recipe_id: int,
        reason: str,
        description: str,
    ) -> RecipeReportEntity:
        ...

    def author_exists(self, author_id: int) -> bool:
        ...

    def follow_author(self, subscriber_id: int, author_id: int) -> None:
        ...

    def unfollow_author(self, subscriber_id: int, author_id: int) -> None:
        ...

    def list_followed_authors(self, subscriber_id: int) -> list[AuthorFollowEntity]:
        ...

    def list_follower_ids(self, author_id: int) -> list[int]:
        ...

    def create_recipe_notifications(
        self,
        user_ids: list[int],
        recipe_id: int,
        recipe_title: str,
        author_username: str | None,
    ) -> None:
        ...

    def list_notifications(self, user_id: int) -> list[NotificationEntity]:
        ...

    def mark_notification_as_read(self, user_id: int, notification_id: int) -> bool:
        ...

    def list_recipes_for_moderation(self, status: str | None = None) -> list[RecipeEntity]:
        ...

    def approve_recipe(self, recipe_id: int, moderation_comment: str) -> RecipeEntity | None:
        ...

    def reject_recipe(self, recipe_id: int, moderation_comment: str) -> RecipeEntity | None:
        ...

    def list_reviews_for_moderation(
        self,
        status: str | None = None,
    ) -> list[RecipeReviewEntity]:
        ...

    def moderate_review(
        self,
        review_id: int,
        moderation_status: str,
        moderation_comment: str,
    ) -> RecipeReviewEntity | None:
        ...

    def list_reports_for_moderation(
        self,
        status: str | None = None,
    ) -> list[RecipeReportEntity]:
        ...

    def moderate_report(
        self,
        report_id: int,
        status: str,
        moderation_comment: str,
    ) -> RecipeReportEntity | None:
        ...
