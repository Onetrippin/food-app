from django.contrib import admin

from app.internal.data.models import AuthorApplicationModel


@admin.register(AuthorApplicationModel)
class AuthorApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "status",
        "subscription_price",
        "subscription_currency",
        "is_subscription_enabled",
        "reviewed_at",
        "created_at",
        "updated_at",
    )
    list_filter = ("status",)
    search_fields = ("user__username", "user__email")
    autocomplete_fields = ("user",)
