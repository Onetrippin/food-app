from django.db import transaction
from django.db.models import Q

from app.internal.data.models import RecipeFavoriteModel, RecipeIngredientModel, RecipeModel
from app.internal.domain.entities.recipe import RecipeEntity


class DjangoRecipeRepository:
    def list(self) -> list[RecipeEntity]:
        recipes = (
            RecipeModel.objects.select_related("author")
            .prefetch_related("ingredients")
            .all()
        )
        return [self._build_entity(recipe) for recipe in recipes]

    def get_by_id(self, recipe_id: int) -> RecipeEntity | None:
        recipe = (
            RecipeModel.objects.select_related("author")
            .prefetch_related("ingredients")
            .filter(id=recipe_id)
            .first()
        )

        if recipe is None:
            return None

        return self._build_entity(recipe)

    def search(self, query: str) -> list[RecipeEntity]:
        normalized_query = query.strip()

        if not normalized_query:
            return self.list()

        recipes = (
            RecipeModel.objects.select_related("author")
            .filter(
                Q(title__icontains=normalized_query)
                | Q(description__icontains=normalized_query)
            )
            .prefetch_related("ingredients")
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

        recipes = (
            RecipeModel.objects.select_related("author")
            .prefetch_related("ingredients")
            .all()
        )
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
    ) -> RecipeEntity:
        recipe = RecipeModel.objects.create(
            author_id=author_id,
            title=title,
            description=description,
        )
        self._replace_ingredients(recipe=recipe, ingredients=ingredients)
        recipe.refresh_from_db()
        recipe = (
            RecipeModel.objects.select_related("author")
            .prefetch_related("ingredients")
            .get(id=recipe.id)
        )
        return self._build_entity(recipe)

    @transaction.atomic
    def update(
        self,
        recipe_id: int,
        title: str,
        description: str,
        ingredients: list[str],
    ) -> RecipeEntity | None:
        recipe = RecipeModel.objects.filter(id=recipe_id).first()

        if recipe is None:
            return None

        recipe.title = title
        recipe.description = description
        recipe.save(update_fields=["title", "description", "updated_at"])
        self._replace_ingredients(recipe=recipe, ingredients=ingredients)
        recipe = (
            RecipeModel.objects.select_related("author")
            .prefetch_related("ingredients")
            .get(id=recipe_id)
        )
        return self._build_entity(recipe)

    def add_to_favorites(self, user_id: int, recipe_id: int) -> None:
        RecipeFavoriteModel.objects.get_or_create(user_id=user_id, recipe_id=recipe_id)

    def remove_from_favorites(self, user_id: int, recipe_id: int) -> None:
        RecipeFavoriteModel.objects.filter(user_id=user_id, recipe_id=recipe_id).delete()

    def list_favorites(self, user_id: int) -> list[RecipeEntity]:
        favorite_recipes = (
            RecipeModel.objects.select_related("author")
            .prefetch_related("ingredients")
            .filter(favorited_by_users__user_id=user_id)
            .distinct()
        )
        return [self._build_entity(recipe) for recipe in favorite_recipes]

    @staticmethod
    def _build_entity(recipe: RecipeModel) -> RecipeEntity:
        return RecipeEntity(
            id=recipe.id,
            title=recipe.title,
            description=recipe.description,
            ingredients=[ingredient.name for ingredient in recipe.ingredients.all()],
            author_id=recipe.author_id,
            author_username=recipe.author.username if recipe.author else None,
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
