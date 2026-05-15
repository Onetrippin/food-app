from app.internal.domain.entities.recipe_analytics import RecipeAnalyticsEntity
from app.internal.domain.entities.recipe import RecipeEntity
from app.internal.domain.interfaces.recipe import RecipeRepositoryInterface


class RecipeService:
    def __init__(self, repository: RecipeRepositoryInterface) -> None:
        self._repository = repository

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
        is_published: bool,
    ) -> RecipeEntity:
        normalized_title = title.strip()

        if not normalized_title:
            raise ValueError("Title is required.")

        normalized_ingredients = self._normalize_ingredients(ingredients)
        self._validate_publish_permission(
            actor_is_staff=actor_is_staff,
            actor_can_publish_recipes=actor_can_publish_recipes,
            is_published=is_published,
        )

        return self._repository.create(
            author_id=author_id,
            title=normalized_title,
            description=description.strip(),
            ingredients=normalized_ingredients,
            is_published=is_published,
        )

    def update_recipe(
        self,
        actor_id: int,
        actor_is_staff: bool,
        actor_can_publish_recipes: bool,
        recipe_id: int,
        title: str,
        description: str,
        ingredients: list[str],
        is_published: bool,
    ) -> RecipeEntity:
        recipe = self.get_recipe(recipe_id=recipe_id)

        if not actor_is_staff and recipe.author_id != actor_id:
            raise PermissionError("You can edit only your own recipes.")

        normalized_title = title.strip()

        if not normalized_title:
            raise ValueError("Title is required.")

        normalized_ingredients = self._normalize_ingredients(ingredients)
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
            is_published=is_published,
        )

        if updated_recipe is None:
            raise ValueError("Recipe not found.")

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
