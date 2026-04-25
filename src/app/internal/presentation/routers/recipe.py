from ninja import Query, Router, Schema

from app.internal.presentation.handlers.recipe import (
    get_recipe_handler,
    list_recipes_handler,
    search_recipes_handler,
)
from app.internal.presentation.handlers.auth import JWTBearerAuth

router = Router(tags=["recipes"])
jwt_bearer_auth = JWTBearerAuth()


class RecipeOutput(Schema):
    id: int
    title: str
    description: str
    created_at: str | None
    updated_at: str | None


@router.get("/", auth=jwt_bearer_auth, response=list[RecipeOutput])
def list_recipes(request):
    return list_recipes_handler()


@router.get("/search", auth=jwt_bearer_auth, response=list[RecipeOutput])
def search_recipes(request, q: str = Query(...)):
    return search_recipes_handler(query=q)


@router.get("/{recipe_id}", auth=jwt_bearer_auth, response=RecipeOutput)
def get_recipe(request, recipe_id: int):
    return get_recipe_handler(recipe_id=recipe_id)
