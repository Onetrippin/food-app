from django.contrib import admin

from app.internal.data.models import (
    AuthorFollowModel,
    NotificationModel,
    RecipeFavoriteModel,
    RecipeIngredientModel,
    RecipeLikeModel,
    RecipeModel,
    RecipeReportModel,
    RecipeReviewModel,
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredientModel
    extra = 1


@admin.register(RecipeModel)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "author",
        "price_amount",
        "price_currency",
        "is_published",
        "views_count",
        "created_at",
        "updated_at",
    )
    search_fields = ("title", "author__username")
    readonly_fields = ("views_count", "created_at", "updated_at")
    inlines = [RecipeIngredientInline]


@admin.register(RecipeFavoriteModel)
class RecipeFavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe", "created_at")
    search_fields = ("user__username", "recipe__title")
    autocomplete_fields = ("user", "recipe")


@admin.register(RecipeLikeModel)
class RecipeLikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe", "created_at")
    search_fields = ("user__username", "recipe__title")
    autocomplete_fields = ("user", "recipe")


@admin.register(RecipeReviewModel)
class RecipeReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe", "user", "rating", "updated_at")
    list_filter = ("rating",)
    search_fields = ("recipe__title", "user__username", "review_text")
    autocomplete_fields = ("recipe", "user")


@admin.register(RecipeReportModel)
class RecipeReportAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe", "user", "reason", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("recipe__title", "user__username", "reason", "description")
    autocomplete_fields = ("recipe", "user")


@admin.register(AuthorFollowModel)
class AuthorFollowAdmin(admin.ModelAdmin):
    list_display = ("id", "subscriber", "author", "created_at")
    search_fields = ("subscriber__username", "author__username")
    autocomplete_fields = ("subscriber", "author")


@admin.register(NotificationModel)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "notification_type", "recipe", "is_read", "created_at")
    list_filter = ("notification_type", "is_read")
    search_fields = ("user__username", "title", "message", "recipe__title")
    autocomplete_fields = ("user", "recipe")
