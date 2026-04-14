from django.contrib import admin

from app.internal.data.models import PasswordChangeCodeModel


@admin.register(PasswordChangeCodeModel)
class PasswordChangeCodeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "expires_at", "used_at", "created_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("code_hash", "created_at", "used_at")
