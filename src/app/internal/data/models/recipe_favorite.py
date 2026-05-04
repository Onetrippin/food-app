from django.conf import settings
from django.db import models


class RecipeFavoriteModel(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorite_recipes",
    )
    recipe = models.ForeignKey(
        "app.RecipeModel",
        on_delete=models.CASCADE,
        related_name="favorited_by_users",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "recipe_favorites"
        ordering = ["-created_at"]
        verbose_name = "Recipe favorite"
        verbose_name_plural = "Recipe favorites"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_user_recipe_favorite",
            )
        ]

    def __str__(self) -> str:
        return f"Favorite recipe {self.recipe_id} for user {self.user_id}"
