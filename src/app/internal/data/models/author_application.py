from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class AuthorApplicationModel(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="author_application",
    )
    motivation = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    subscription_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    subscription_currency = models.CharField(max_length=3, default="RUB")
    is_subscription_enabled = models.BooleanField(default=False)
    review_comment = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "author_applications"
        ordering = ["-updated_at"]
        verbose_name = "Author application"
        verbose_name_plural = "Author applications"

    def __str__(self) -> str:
        return f"Author application for user {self.user_id}"
