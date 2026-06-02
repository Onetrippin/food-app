from django.conf import settings
from django.db import models


class RecipeReportModel(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        REVIEWED = "reviewed", "Reviewed"
        REJECTED = "rejected", "Rejected"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recipe_reports",
    )
    recipe = models.ForeignKey(
        "app.RecipeModel",
        on_delete=models.CASCADE,
        related_name="reports",
    )
    reason = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    moderation_comment = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "recipe_reports"
        ordering = ["-created_at"]
        verbose_name = "Recipe report"
        verbose_name_plural = "Recipe reports"

    def __str__(self) -> str:
        return f"Report for recipe {self.recipe_id} by user {self.user_id}"
