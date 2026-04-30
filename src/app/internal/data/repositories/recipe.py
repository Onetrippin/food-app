from django.db.models import Q

from app.internal.data.models import RecipeModel
from app.internal.domain.entities.recipe import RecipeEntity


class DjangoRecipeRepository:
    def list(self) -> list[RecipeEntity]:
        recipes = RecipeModel.objects.prefetch_related("ingredients").all()
        return [self._build_entity(recipe) for recipe in recipes]

    def get_by_id(self, recipe_id: int) -> RecipeEntity | None:
        recipe = RecipeModel.objects.prefetch_related("ingredients").filter(id=recipe_id).first()

        if recipe is None:
            return None

        return self._build_entity(recipe)

    def search(self, query: str) -> list[RecipeEntity]:
        normalized_query = query.strip()

        if not normalized_query:
            return self.list()

        recipes = RecipeModel.objects.filter(
            Q(title__icontains=normalized_query)
            | Q(description__icontains=normalized_query)
        ).prefetch_related("ingredients")
        return [self._build_entity(recipe) for recipe in recipes]

    def find_by_ingredients(self, available_ingredients: list[str]) -> list[RecipeEntity]:
        normalized_available_ingredients = {
            ingredient.strip().lower()
            for ingredient in available_ingredients
            if ingredient.strip()
        }

        if not normalized_available_ingredients:
            return []

        recipes = RecipeModel.objects.prefetch_related("ingredients").all()
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

    @staticmethod
    def _build_entity(recipe: RecipeModel) -> RecipeEntity:
        return RecipeEntity(
            id=recipe.id,
            title=recipe.title,
            description=recipe.description,
            ingredients=[ingredient.name for ingredient in recipe.ingredients.all()],
            created_at=recipe.created_at,
            updated_at=recipe.updated_at,
        )
