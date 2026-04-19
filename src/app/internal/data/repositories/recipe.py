from app.internal.data.models import RecipeModel
from app.internal.domain.entities.recipe import RecipeEntity


class DjangoRecipeRepository:
    def list(self) -> list[RecipeEntity]:
        recipes = RecipeModel.objects.all()

        return [
            RecipeEntity(
                id=recipe.id,
                title=recipe.title,
                description=recipe.description,
                created_at=recipe.created_at,
                updated_at=recipe.updated_at,
            )
            for recipe in recipes
        ]
