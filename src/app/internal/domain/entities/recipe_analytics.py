from dataclasses import dataclass

from app.internal.domain.entities.recipe import RecipeEntity


@dataclass(slots=True, kw_only=True)
class RecipeAnalyticsEntity:
    total_recipes: int
    published_recipes: int
    total_views: int
    total_likes: int
    total_favorites: int
    recipes: list[RecipeEntity]
