from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class PaymentModel(models.Model):
    class PaymentType(models.TextChoices):
        RECIPE_PURCHASE = "recipe_purchase", "Recipe purchase"
        AUTHOR_SUBSCRIPTION = "author_subscription", "Author subscription"

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCEEDED = "succeeded", "Succeeded"
        CANCELED = "canceled", "Canceled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    recipe = models.ForeignKey(
        "app.RecipeModel",
        on_delete=models.CASCADE,
        related_name="payments",
        null=True,
        blank=True,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="author_subscription_payments",
        null=True,
        blank=True,
    )
    payment_type = models.CharField(max_length=32, choices=PaymentType.choices)
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    currency = models.CharField(max_length=3, default="RUB")
    description = models.CharField(max_length=255)
    yookassa_payment_id = models.CharField(max_length=128, unique=True)
    confirmation_url = models.URLField(blank=True)
    payment_method_id = models.CharField(max_length=128, blank=True)
    save_payment_method = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payments"
        ordering = ["-created_at"]
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self) -> str:
        return f"{self.payment_type}:{self.yookassa_payment_id}"
