from django.contrib import admin

from app.internal.data.models import RecipeModel


@admin.register(RecipeModel)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_at", "updated_at")
    search_fields = ("title",)
    readonly_fields = ("created_at", "updated_at")
