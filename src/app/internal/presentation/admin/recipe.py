from django.contrib import admin

from app.internal.data.models import (
    RecipeFavoriteModel,
    RecipeIngredientModel,
    RecipeLikeModel,
    RecipeModel,
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredientModel
    extra = 1


@admin.register(RecipeModel)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "is_published", "views_count", "created_at", "updated_at")
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
