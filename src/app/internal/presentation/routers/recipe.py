from ninja import Query, Router, Schema
from pydantic import Field

from app.internal.presentation.handlers.recipe import (
    add_recipe_to_favorites_handler,
    add_recipe_like_handler,
    add_recipe_review_handler,
    create_recipe_handler,
    delete_recipe_handler,
    find_recipes_by_ingredients_handler,
    follow_author_handler,
    get_author_recipe_analytics_handler,
    get_recipe_for_view_handler,
    list_recipes_handler,
    list_favorite_recipes_handler,
    list_followed_authors_handler,
    list_notifications_handler,
    list_recipe_reviews_handler,
    mark_notification_as_read_handler,
    remove_recipe_from_favorites_handler,
    remove_recipe_like_handler,
    report_recipe_handler,
    search_recipes_handler,
    unfollow_author_handler,
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
    price_amount: str
    price_currency: str
    has_access: bool
    is_published: bool
    views_count: int
    likes_count: int
    favorites_count: int
    average_rating: str | None
    reviews_count: int
    created_at: str | None
    updated_at: str | None


class RecipeInput(Schema):
    title: str
    description: str = ""
    ingredients: list[str] = Field(default_factory=list)
    price_amount: str = "0.00"
    price_currency: str = "RUB"
    is_published: bool = True


class MessageOutput(Schema):
    detail: str


class RecipeReviewInput(Schema):
    rating: int
    review_text: str = ""


class RecipeReviewOutput(Schema):
    user_id: int
    username: str
    recipe_id: int
    rating: int
    review_text: str
    created_at: str
    updated_at: str


class RecipeReportInput(Schema):
    reason: str
    description: str = ""


class AuthorFollowOutput(Schema):
    subscriber_id: int
    author_id: int
    author_username: str
    created_at: str


class NotificationOutput(Schema):
    id: int
    user_id: int
    notification_type: str
    title: str
    message: str
    recipe_id: int | None
    is_read: bool
    created_at: str
    read_at: str | None


class RecipeAnalyticsOutput(Schema):
    total_recipes: int
    published_recipes: int
    total_views: int
    total_likes: int
    total_favorites: int
    recipes: list[RecipeOutput]


@router.get("/", auth=jwt_bearer_auth, response=list[RecipeOutput])
def list_recipes(request):
    return list_recipes_handler(user_id=request.auth.id, user_is_staff=request.auth.is_staff)


@router.get("/search", auth=jwt_bearer_auth, response=list[RecipeOutput])
def search_recipes(request, q: str = Query(...)):
    return search_recipes_handler(
        query=q,
        user_id=request.auth.id,
        user_is_staff=request.auth.is_staff,
    )


@router.get("/search/by-ingredients", auth=jwt_bearer_auth, response=list[RecipeOutput])
def find_recipes_by_ingredients(request, ingredients: str = Query(...)):
    available_ingredients = [
        ingredient.strip()
        for ingredient in ingredients.split(",")
        if ingredient.strip()
    ]
    return find_recipes_by_ingredients_handler(
        available_ingredients=available_ingredients,
        user_id=request.auth.id,
        user_is_staff=request.auth.is_staff,
    )


@router.get("/favorites", auth=jwt_bearer_auth, response=list[RecipeOutput])
def list_favorite_recipes(request):
    return list_favorite_recipes_handler(user_id=request.auth.id)


@router.get("/analytics", auth=jwt_bearer_auth, response=RecipeAnalyticsOutput)
def get_author_recipe_analytics(request):
    return get_author_recipe_analytics_handler(author_id=request.auth.id)


@router.get("/authors/follows", auth=jwt_bearer_auth, response=list[AuthorFollowOutput])
def list_followed_authors(request):
    return list_followed_authors_handler(subscriber_id=request.auth.id)


@router.post("/authors/{author_id}/follow", auth=jwt_bearer_auth, response=MessageOutput)
def follow_author(request, author_id: int):
    return follow_author_handler(subscriber_id=request.auth.id, author_id=author_id)


@router.delete("/authors/{author_id}/follow", auth=jwt_bearer_auth, response=MessageOutput)
def unfollow_author(request, author_id: int):
    return unfollow_author_handler(subscriber_id=request.auth.id, author_id=author_id)


@router.get("/notifications", auth=jwt_bearer_auth, response=list[NotificationOutput])
def list_notifications(request):
    return list_notifications_handler(user_id=request.auth.id)


@router.post(
    "/notifications/{notification_id}/read",
    auth=jwt_bearer_auth,
    response=MessageOutput,
)
def mark_notification_as_read(request, notification_id: int):
    return mark_notification_as_read_handler(
        user_id=request.auth.id,
        notification_id=notification_id,
    )


@router.post("/", auth=jwt_bearer_auth, response=RecipeOutput)
def create_recipe(request, payload: RecipeInput):
    return create_recipe_handler(
        author_id=request.auth.id,
        actor_is_staff=request.auth.is_staff,
        actor_can_publish_recipes=request.auth.can_publish_recipes,
        title=payload.title,
        description=payload.description,
        ingredients=payload.ingredients,
        price_amount=payload.price_amount,
        price_currency=payload.price_currency,
        is_published=payload.is_published,
    )


@router.put("/{recipe_id}", auth=jwt_bearer_auth, response=RecipeOutput)
def update_recipe(request, recipe_id: int, payload: RecipeInput):
    return update_recipe_handler(
        actor_id=request.auth.id,
        actor_is_staff=request.auth.is_staff,
        actor_can_publish_recipes=request.auth.can_publish_recipes,
        recipe_id=recipe_id,
        title=payload.title,
        description=payload.description,
        ingredients=payload.ingredients,
        price_amount=payload.price_amount,
        price_currency=payload.price_currency,
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


@router.get("/{recipe_id}/reviews", auth=jwt_bearer_auth, response=list[RecipeReviewOutput])
def list_recipe_reviews(request, recipe_id: int):
    return list_recipe_reviews_handler(
        recipe_id=recipe_id,
        actor_id=request.auth.id,
        actor_is_staff=request.auth.is_staff,
    )


@router.post("/{recipe_id}/reviews", auth=jwt_bearer_auth, response=RecipeReviewOutput)
def add_recipe_review(request, recipe_id: int, payload: RecipeReviewInput):
    return add_recipe_review_handler(
        user_id=request.auth.id,
        user_is_staff=request.auth.is_staff,
        recipe_id=recipe_id,
        rating=payload.rating,
        review_text=payload.review_text,
    )


@router.post("/{recipe_id}/report", auth=jwt_bearer_auth, response=MessageOutput)
def report_recipe(request, recipe_id: int, payload: RecipeReportInput):
    return report_recipe_handler(
        user_id=request.auth.id,
        recipe_id=recipe_id,
        reason=payload.reason,
        description=payload.description,
    )


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
