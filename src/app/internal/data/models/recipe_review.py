from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class RecipeReviewModel(models.Model):
    class ModerationStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recipe_reviews",
    )
    recipe = models.ForeignKey(
        "app.RecipeModel",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review_text = models.TextField(blank=True)
    moderation_status = models.CharField(
        max_length=20,
        choices=ModerationStatus.choices,
        default=ModerationStatus.PENDING,
    )
    moderation_comment = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "recipe_reviews"
        ordering = ["-updated_at"]
        verbose_name = "Recipe review"
        verbose_name_plural = "Recipe reviews"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_user_recipe_review",
            )
        ]

    def __str__(self) -> str:
        return f"Review for recipe {self.recipe_id} by user {self.user_id}"
