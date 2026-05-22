from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class AuthorSubscriptionModel(models.Model):
    subscriber = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="author_subscriptions",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscribers",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    currency = models.CharField(max_length=3, default="RUB")
    payment_method_id = models.CharField(max_length=128, blank=True)
    started_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "author_subscriptions"
        ordering = ["-expires_at"]
        verbose_name = "Author subscription"
        verbose_name_plural = "Author subscriptions"

    def __str__(self) -> str:
        return f"Subscription author {self.author_id} subscriber {self.subscriber_id}"
