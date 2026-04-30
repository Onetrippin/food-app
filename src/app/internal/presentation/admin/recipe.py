from django.contrib import admin

from app.internal.data.models import RecipeIngredientModel, RecipeModel


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredientModel
    extra = 1


@admin.register(RecipeModel)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_at", "updated_at")
    search_fields = ("title",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [RecipeIngredientInline]
