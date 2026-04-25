from django.db.models import Q

from app.internal.data.models import RecipeModel
from app.internal.domain.entities.recipe import RecipeEntity


class DjangoRecipeRepository:
    def list(self) -> list[RecipeEntity]:
        recipes = RecipeModel.objects.all()
        return [self._build_entity(recipe) for recipe in recipes]

    def get_by_id(self, recipe_id: int) -> RecipeEntity | None:
        recipe = RecipeModel.objects.filter(id=recipe_id).first()

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
        )
        return [self._build_entity(recipe) for recipe in recipes]

    @staticmethod
    def _build_entity(recipe: RecipeModel) -> RecipeEntity:
        return RecipeEntity(
            id=recipe.id,
            title=recipe.title,
            description=recipe.description,
            created_at=recipe.created_at,
            updated_at=recipe.updated_at,
        )
