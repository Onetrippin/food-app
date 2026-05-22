from django.contrib import admin

from app.internal.data.models import (
    AuthorSubscriptionModel,
    PaymentModel,
    RecipePurchaseModel,
)


@admin.register(PaymentModel)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "payment_type",
        "status",
        "user",
        "recipe",
        "author",
        "amount",
        "currency",
        "created_at",
    )
    list_filter = ("payment_type", "status", "currency")
    search_fields = ("yookassa_payment_id", "user__username", "recipe__title", "author__username")
    autocomplete_fields = ("user", "recipe", "author")
    readonly_fields = ("yookassa_payment_id", "confirmation_url", "payment_method_id", "paid_at")


@admin.register(RecipePurchaseModel)
class RecipePurchaseAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe", "payment", "purchased_at")
    search_fields = ("user__username", "recipe__title", "payment__yookassa_payment_id")
    autocomplete_fields = ("user", "recipe", "payment")


@admin.register(AuthorSubscriptionModel)
class AuthorSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "subscriber", "author", "amount", "currency", "started_at", "expires_at")
    search_fields = ("subscriber__username", "author__username", "payment_method_id")
    autocomplete_fields = ("subscriber", "author")
