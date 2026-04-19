from app.internal.domain.entities.recipe import RecipeEntity
from app.internal.domain.interfaces.recipe import RecipeRepositoryInterface


class RecipeService:
    def __init__(self, repository: RecipeRepositoryInterface) -> None:
        self._repository = repository

    def list_recipes(self) -> list[RecipeEntity]:
        return self._repository.list()
