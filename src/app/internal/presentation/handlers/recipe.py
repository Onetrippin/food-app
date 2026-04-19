from app.internal.data.repositories.recipe import DjangoRecipeRepository
from app.internal.domain.services.recipe import RecipeService


def list_recipes_handler() -> list[dict[str, object]]:
    service = RecipeService(repository=DjangoRecipeRepository())

    return [
        {
            "id": recipe.id,
            "title": recipe.title,
            "description": recipe.description,
            "created_at": recipe.created_at.isoformat() if recipe.created_at else None,
            "updated_at": recipe.updated_at.isoformat() if recipe.updated_at else None,
        }
        for recipe in service.list_recipes()
    ]
