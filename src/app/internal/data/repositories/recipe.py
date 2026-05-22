from django.db import transaction
from django.db.models import Count, F, Q
from decimal import Decimal

from app.internal.data.models import (
    RecipeFavoriteModel,
    RecipeIngredientModel,
    RecipeLikeModel,
    RecipeModel,
)
from app.internal.domain.entities.recipe import RecipeEntity


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
            )
            .distinct()
        )
