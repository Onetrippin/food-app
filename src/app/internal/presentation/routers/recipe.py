from ninja import Query, Router, Schema
from pydantic import Field

from app.internal.presentation.handlers.recipe import (
    add_recipe_to_favorites_handler,
    add_recipe_like_handler,
    create_recipe_handler,
    delete_recipe_handler,
    find_recipes_by_ingredients_handler,
    get_author_recipe_analytics_handler,
    get_recipe_handler,
    get_recipe_for_view_handler,
    list_recipes_handler,
    list_favorite_recipes_handler,
    remove_recipe_from_favorites_handler,
    remove_recipe_like_handler,
    search_recipes_handler,
    update_recipe_handler,
)
from app.internal.presentation.handlers.auth import JWTBearerAuth

router = Router(tags=["recipes"])
jwt_bearer_auth = JWTBearerAuth()


class RecipeOutput(Schema):
    id: int
    title: str
    description: str
    ingredients: list[str]
    author_id: int | None
    author_username: str | None
    is_published: bool
    views_count: int
    likes_count: int
    favorites_count: int
    created_at: str | None
    updated_at: str | None


class RecipeInput(Schema):
    title: str
    description: str = ""
    ingredients: list[str] = Field(default_factory=list)
    is_published: bool = True


class MessageOutput(Schema):
    detail: str


class RecipeAnalyticsOutput(Schema):
    total_recipes: int
    published_recipes: int
    total_views: int
    total_likes: int
    total_favorites: int
    recipes: list[RecipeOutput]


@router.get("/", auth=jwt_bearer_auth, response=list[RecipeOutput])
def list_recipes(request):
    return list_recipes_handler()


@router.get("/search", auth=jwt_bearer_auth, response=list[RecipeOutput])
def search_recipes(request, q: str = Query(...)):
    return search_recipes_handler(query=q)


@router.get("/search/by-ingredients", auth=jwt_bearer_auth, response=list[RecipeOutput])
def find_recipes_by_ingredients(request, ingredients: str = Query(...)):
    available_ingredients = [
        ingredient.strip()
        for ingredient in ingredients.split(",")
        if ingredient.strip()
    ]
    return find_recipes_by_ingredients_handler(
        available_ingredients=available_ingredients
    )


@router.get("/favorites", auth=jwt_bearer_auth, response=list[RecipeOutput])
def list_favorite_recipes(request):
    return list_favorite_recipes_handler(user_id=request.auth.id)


@router.get("/analytics", auth=jwt_bearer_auth, response=RecipeAnalyticsOutput)
def get_author_recipe_analytics(request):
    return get_author_recipe_analytics_handler(author_id=request.auth.id)


@router.post("/", auth=jwt_bearer_auth, response=RecipeOutput)
def create_recipe(request, payload: RecipeInput):
    return create_recipe_handler(
        author_id=request.auth.id,
        title=payload.title,
        description=payload.description,
        ingredients=payload.ingredients,
        is_published=payload.is_published,
    )


@router.put("/{recipe_id}", auth=jwt_bearer_auth, response=RecipeOutput)
def update_recipe(request, recipe_id: int, payload: RecipeInput):
    return update_recipe_handler(
        actor_id=request.auth.id,
        actor_is_staff=request.auth.is_staff,
        recipe_id=recipe_id,
        title=payload.title,
        description=payload.description,
        ingredients=payload.ingredients,
        is_published=payload.is_published,
    )


@router.post("/{recipe_id}/favorite", auth=jwt_bearer_auth, response=MessageOutput)
def add_recipe_to_favorites(request, recipe_id: int):
    return add_recipe_to_favorites_handler(user_id=request.auth.id, recipe_id=recipe_id)


@router.delete("/{recipe_id}/favorite", auth=jwt_bearer_auth, response=MessageOutput)
def remove_recipe_from_favorites(request, recipe_id: int):
    return remove_recipe_from_favorites_handler(
        user_id=request.auth.id,
        recipe_id=recipe_id,
    )


@router.post("/{recipe_id}/like", auth=jwt_bearer_auth, response=MessageOutput)
def add_recipe_like(request, recipe_id: int):
    return add_recipe_like_handler(user_id=request.auth.id, recipe_id=recipe_id)


@router.delete("/{recipe_id}/like", auth=jwt_bearer_auth, response=MessageOutput)
def remove_recipe_like(request, recipe_id: int):
    return remove_recipe_like_handler(user_id=request.auth.id, recipe_id=recipe_id)


@router.delete("/{recipe_id}", auth=jwt_bearer_auth, response=MessageOutput)
def delete_recipe(request, recipe_id: int):
    return delete_recipe_handler(
        actor_id=request.auth.id,
        actor_is_staff=request.auth.is_staff,
        recipe_id=recipe_id,
    )


@router.get("/{recipe_id}", auth=jwt_bearer_auth, response=RecipeOutput)
def get_recipe(request, recipe_id: int):
    return get_recipe_for_view_handler(
        recipe_id=recipe_id,
        actor_id=request.auth.id,
        actor_is_staff=request.auth.is_staff,
    )
