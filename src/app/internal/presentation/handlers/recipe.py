from ninja.errors import HttpError

from app.internal.data.repositories.payment import DjangoPaymentRepository
from app.internal.data.repositories.recipe import DjangoRecipeRepository
from app.internal.domain.entities.author_follow import AuthorFollowEntity
from app.internal.domain.entities.notification import NotificationEntity
from app.internal.domain.entities.recipe import RecipeEntity
from app.internal.domain.entities.recipe_review import RecipeReviewEntity
from app.internal.domain.services.recipe import RecipeService


def list_recipes_handler(user_id: int, user_is_staff: bool) -> list[dict[str, object]]:
    service = RecipeService(
        repository=DjangoRecipeRepository(),
        payment_repository=DjangoPaymentRepository(),
    )
    return [
        _serialize_recipe(recipe, user_id=user_id, user_is_staff=user_is_staff)
        for recipe in service.list_recipes()
    ]


def get_recipe_handler(recipe_id: int) -> dict[str, object]:
    service = RecipeService(
        repository=DjangoRecipeRepository(),
        payment_repository=DjangoPaymentRepository(),
    )

    try:
        recipe = service.get_recipe(recipe_id=recipe_id)
    except ValueError as error:
        raise HttpError(404, str(error)) from error

    return _serialize_recipe(recipe, user_id=recipe.author_id or 0, user_is_staff=False)


def get_recipe_for_view_handler(
    recipe_id: int,
    actor_id: int,
    actor_is_staff: bool,
) -> dict[str, object]:
    service = RecipeService(
        repository=DjangoRecipeRepository(),
        payment_repository=DjangoPaymentRepository(),
    )

    try:
        recipe = service.get_recipe_for_view(
            recipe_id=recipe_id,
            actor_id=actor_id,
            actor_is_staff=actor_is_staff,
        )
    except PermissionError as error:
        status_code = 402 if "purchase" in str(error).lower() or "subscription" in str(error).lower() else 403
        raise HttpError(status_code, str(error)) from error
    except ValueError as error:
        raise HttpError(404, str(error)) from error

    return _serialize_recipe(recipe, user_id=actor_id, user_is_staff=actor_is_staff)


def search_recipes_handler(query: str, user_id: int, user_is_staff: bool) -> list[dict[str, object]]:
    service = RecipeService(
        repository=DjangoRecipeRepository(),
        payment_repository=DjangoPaymentRepository(),
    )
    return [
        _serialize_recipe(recipe, user_id=user_id, user_is_staff=user_is_staff)
        for recipe in service.search_recipes(query=query)
    ]


def find_recipes_by_ingredients_handler(
    available_ingredients: list[str],
    user_id: int,
    user_is_staff: bool,
) -> list[dict[str, object]]:
    service = RecipeService(
        repository=DjangoRecipeRepository(),
        payment_repository=DjangoPaymentRepository(),
    )

    try:
        recipes = service.find_recipes_by_ingredients(
            available_ingredients=available_ingredients
        )
    except ValueError as error:
        raise HttpError(400, str(error)) from error

    return [
        _serialize_recipe(recipe, user_id=user_id, user_is_staff=user_is_staff)
        for recipe in recipes
    ]


def create_recipe_handler(
    author_id: int,
    actor_is_staff: bool,
    actor_can_publish_recipes: bool,
    title: str,
    description: str,
    ingredients: list[str],
    price_amount: str,
    price_currency: str,
    is_published: bool,
) -> dict[str, object]:
    service = RecipeService(
        repository=DjangoRecipeRepository(),
        payment_repository=DjangoPaymentRepository(),
    )

    try:
        recipe = service.create_recipe(
            author_id=author_id,
            actor_is_staff=actor_is_staff,
            actor_can_publish_recipes=actor_can_publish_recipes,
            title=title,
            description=description,
            ingredients=ingredients,
            price_amount=price_amount,
            price_currency=price_currency,
            is_published=is_published,
        )
    except PermissionError as error:
        raise HttpError(403, str(error)) from error
    except ValueError as error:
        raise HttpError(400, str(error)) from error

    return _serialize_recipe(recipe, user_id=author_id, user_is_staff=actor_is_staff)


def update_recipe_handler(
    actor_id: int,
    actor_is_staff: bool,
    actor_can_publish_recipes: bool,
    recipe_id: int,
    title: str,
    description: str,
    ingredients: list[str],
    price_amount: str,
    price_currency: str,
    is_published: bool,
) -> dict[str, object]:
    service = RecipeService(
        repository=DjangoRecipeRepository(),
        payment_repository=DjangoPaymentRepository(),
    )

    try:
        recipe = service.update_recipe(
            actor_id=actor_id,
            actor_is_staff=actor_is_staff,
            actor_can_publish_recipes=actor_can_publish_recipes,
            recipe_id=recipe_id,
            title=title,
            description=description,
            ingredients=ingredients,
            price_amount=price_amount,
            price_currency=price_currency,
            is_published=is_published,
        )
    except PermissionError as error:
        raise HttpError(403, str(error)) from error
    except ValueError as error:
        status_code = 404 if str(error) == "Recipe not found." else 400
        raise HttpError(status_code, str(error)) from error

    return _serialize_recipe(recipe, user_id=actor_id, user_is_staff=actor_is_staff)


def add_recipe_to_favorites_handler(user_id: int, recipe_id: int) -> dict[str, str]:
    service = RecipeService(
        repository=DjangoRecipeRepository(),
        payment_repository=DjangoPaymentRepository(),
    )

    try:
        service.add_recipe_to_favorites(user_id=user_id, recipe_id=recipe_id)
    except ValueError as error:
        raise HttpError(404, str(error)) from error

    return {"detail": "Recipe added to favorites."}


def remove_recipe_from_favorites_handler(user_id: int, recipe_id: int) -> dict[str, str]:
    service = RecipeService(
        repository=DjangoRecipeRepository(),
        payment_repository=DjangoPaymentRepository(),
    )

    try:
        service.remove_recipe_from_favorites(user_id=user_id, recipe_id=recipe_id)
    except ValueError as error:
        raise HttpError(404, str(error)) from error

    return {"detail": "Recipe removed from favorites."}


def list_favorite_recipes_handler(user_id: int) -> list[dict[str, object]]:
    service = RecipeService(
        repository=DjangoRecipeRepository(),
        payment_repository=DjangoPaymentRepository(),
    )
    return [
        _serialize_recipe(recipe, user_id=user_id, user_is_staff=False)
        for recipe in service.list_favorite_recipes(user_id=user_id)
    ]


def add_recipe_like_handler(user_id: int, recipe_id: int) -> dict[str, str]:
    service = RecipeService(
        repository=DjangoRecipeRepository(),
        payment_repository=DjangoPaymentRepository(),
    )

    try:
        service.add_recipe_like(user_id=user_id, recipe_id=recipe_id)
    except ValueError as error:
        status_code = 404 if str(error) == "Recipe not found." else 400
        raise HttpError(status_code, str(error)) from error

    return {"detail": "Recipe liked."}


def remove_recipe_like_handler(user_id: int, recipe_id: int) -> dict[str, str]:
    service = RecipeService(
        repository=DjangoRecipeRepository(),
        payment_repository=DjangoPaymentRepository(),
    )

    try:
        service.remove_recipe_like(user_id=user_id, recipe_id=recipe_id)
    except ValueError as error:
        raise HttpError(404, str(error)) from error

    return {"detail": "Recipe unliked."}


def delete_recipe_handler(actor_id: int, actor_is_staff: bool, recipe_id: int) -> dict[str, str]:
    service = RecipeService(
        repository=DjangoRecipeRepository(),
        payment_repository=DjangoPaymentRepository(),
    )

    try:
        service.delete_recipe(
            actor_id=actor_id,
            actor_is_staff=actor_is_staff,
            recipe_id=recipe_id,
        )
    except PermissionError as error:
        raise HttpError(403, str(error)) from error
    except ValueError as error:
        raise HttpError(404, str(error)) from error

    return {"detail": "Recipe deleted successfully."}


def get_author_recipe_analytics_handler(author_id: int) -> dict[str, object]:
    service = RecipeService(
        repository=DjangoRecipeRepository(),
        payment_repository=DjangoPaymentRepository(),
    )
    analytics = service.get_author_analytics(author_id=author_id)

    return {
        "total_recipes": analytics.total_recipes,
        "published_recipes": analytics.published_recipes,
        "total_views": analytics.total_views,
        "total_likes": analytics.total_likes,
        "total_favorites": analytics.total_favorites,
        "recipes": [
            _serialize_recipe(recipe, user_id=author_id, user_is_staff=False)
            for recipe in analytics.recipes
        ],
    }


def list_recipe_reviews_handler(
    recipe_id: int,
    actor_id: int,
    actor_is_staff: bool,
) -> list[dict[str, object]]:
    service = RecipeService(
        repository=DjangoRecipeRepository(),
        payment_repository=DjangoPaymentRepository(),
    )

    try:
        reviews = service.list_recipe_reviews(
            recipe_id=recipe_id,
            actor_id=actor_id,
            actor_is_staff=actor_is_staff,
        )
    except PermissionError as error:
        raise HttpError(403, str(error)) from error
    except ValueError as error:
        raise HttpError(404, str(error)) from error

    return [_serialize_review(review) for review in reviews]


def add_recipe_review_handler(
    user_id: int,
    user_is_staff: bool,
    recipe_id: int,
    rating: int,
    review_text: str,
) -> dict[str, object]:
    service = RecipeService(
        repository=DjangoRecipeRepository(),
        payment_repository=DjangoPaymentRepository(),
    )

    try:
        review = service.add_recipe_review(
            user_id=user_id,
            actor_is_staff=user_is_staff,
            recipe_id=recipe_id,
            rating=rating,
            review_text=review_text,
        )
    except PermissionError as error:
        status_code = 402 if "purchase" in str(error).lower() or "subscription" in str(error).lower() else 403
        raise HttpError(status_code, str(error)) from error
    except ValueError as error:
        status_code = 404 if str(error) == "Recipe not found." else 400
        raise HttpError(status_code, str(error)) from error

    return _serialize_review(review)


def report_recipe_handler(
    user_id: int,
    recipe_id: int,
    reason: str,
    description: str,
) -> dict[str, str]:
    service = RecipeService(
        repository=DjangoRecipeRepository(),
        payment_repository=DjangoPaymentRepository(),
    )

    try:
        service.report_recipe(
            user_id=user_id,
            recipe_id=recipe_id,
            reason=reason,
            description=description,
        )
    except PermissionError as error:
        raise HttpError(403, str(error)) from error
    except ValueError as error:
        status_code = 404 if str(error) == "Recipe not found." else 400
        raise HttpError(status_code, str(error)) from error

    return {"detail": "Recipe report submitted."}


def follow_author_handler(subscriber_id: int, author_id: int) -> dict[str, str]:
    service = RecipeService(
        repository=DjangoRecipeRepository(),
        payment_repository=DjangoPaymentRepository(),
    )

    try:
        service.follow_author(subscriber_id=subscriber_id, author_id=author_id)
    except ValueError as error:
        status_code = 404 if str(error) == "Author not found." else 400
        raise HttpError(status_code, str(error)) from error

    return {"detail": "Author followed."}


def unfollow_author_handler(subscriber_id: int, author_id: int) -> dict[str, str]:
    service = RecipeService(
        repository=DjangoRecipeRepository(),
        payment_repository=DjangoPaymentRepository(),
    )

    try:
        service.unfollow_author(subscriber_id=subscriber_id, author_id=author_id)
    except ValueError as error:
        status_code = 404 if str(error) == "Author not found." else 400
        raise HttpError(status_code, str(error)) from error

    return {"detail": "Author unfollowed."}


def list_followed_authors_handler(subscriber_id: int) -> list[dict[str, object]]:
    service = RecipeService(
        repository=DjangoRecipeRepository(),
        payment_repository=DjangoPaymentRepository(),
    )
    follows = service.list_followed_authors(subscriber_id=subscriber_id)
    return [_serialize_follow(follow) for follow in follows]


def list_notifications_handler(user_id: int) -> list[dict[str, object]]:
    service = RecipeService(
        repository=DjangoRecipeRepository(),
        payment_repository=DjangoPaymentRepository(),
    )
    notifications = service.list_notifications(user_id=user_id)
    return [_serialize_notification(notification) for notification in notifications]


def mark_notification_as_read_handler(user_id: int, notification_id: int) -> dict[str, str]:
    service = RecipeService(
        repository=DjangoRecipeRepository(),
        payment_repository=DjangoPaymentRepository(),
    )

    try:
        service.mark_notification_as_read(
            user_id=user_id,
            notification_id=notification_id,
        )
    except ValueError as error:
        raise HttpError(404, str(error)) from error

    return {"detail": "Notification marked as read."}


def _serialize_recipe(recipe: RecipeEntity, user_id: int, user_is_staff: bool) -> dict[str, object]:
    payment_repository = DjangoPaymentRepository()
    has_access = _has_recipe_access(
        recipe=recipe,
        user_id=user_id,
        user_is_staff=user_is_staff,
        payment_repository=payment_repository,
    )

    return {
        "id": recipe.id,
        "title": recipe.title,
        "description": recipe.description if has_access else "",
        "ingredients": recipe.ingredients or [] if has_access else [],
        "author_id": recipe.author_id,
        "author_username": recipe.author_username,
        "price_amount": f"{recipe.price_amount:.2f}",
        "price_currency": recipe.price_currency,
        "has_access": has_access,
        "is_published": recipe.is_published,
        "views_count": recipe.views_count,
        "likes_count": recipe.likes_count,
        "favorites_count": recipe.favorites_count,
        "average_rating": (
            f"{recipe.average_rating:.2f}" if recipe.average_rating is not None else None
        ),
        "reviews_count": recipe.reviews_count,
        "created_at": recipe.created_at.isoformat() if recipe.created_at else None,
        "updated_at": recipe.updated_at.isoformat() if recipe.updated_at else None,
    }


def _has_recipe_access(
    recipe: RecipeEntity,
    user_id: int,
    user_is_staff: bool,
    payment_repository: DjangoPaymentRepository,
) -> bool:
    if recipe.price_amount <= 0:
        return True

    if user_is_staff or recipe.author_id == user_id:
        return True

    if user_id <= 0 or recipe.id is None:
        return False

    return payment_repository.has_recipe_access(
        user_id=user_id,
        recipe_id=recipe.id,
        author_id=recipe.author_id,
    )


def _serialize_review(review: RecipeReviewEntity) -> dict[str, object]:
    return {
        "user_id": review.user_id,
        "username": review.username,
        "recipe_id": review.recipe_id,
        "rating": review.rating,
        "review_text": review.review_text,
        "created_at": review.created_at.isoformat(),
        "updated_at": review.updated_at.isoformat(),
    }


def _serialize_follow(follow: AuthorFollowEntity) -> dict[str, object]:
    return {
        "subscriber_id": follow.subscriber_id,
        "author_id": follow.author_id,
        "author_username": follow.author_username,
        "created_at": follow.created_at.isoformat(),
    }


def _serialize_notification(notification: NotificationEntity) -> dict[str, object]:
    return {
        "id": notification.id,
        "user_id": notification.user_id,
        "notification_type": notification.notification_type,
        "title": notification.title,
        "message": notification.message,
        "recipe_id": notification.recipe_id,
        "is_read": notification.is_read,
        "created_at": notification.created_at.isoformat(),
        "read_at": notification.read_at.isoformat() if notification.read_at else None,
    }
