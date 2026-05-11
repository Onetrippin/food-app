from django.conf import settings
from django.db import models


class RecipeLikeModel(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="liked_recipes",
    )
    recipe = models.ForeignKey(
        "app.RecipeModel",
        on_delete=models.CASCADE,
        related_name="liked_by_users",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "recipe_likes"
        ordering = ["-created_at"]
        verbose_name = "Recipe like"
        verbose_name_plural = "Recipe likes"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_user_recipe_like",
            )
        ]

    def __str__(self) -> str:
        return f"Like for recipe {self.recipe_id} by user {self.user_id}"
