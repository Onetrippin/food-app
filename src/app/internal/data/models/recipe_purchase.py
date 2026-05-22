from django.conf import settings
from django.db import models


class RecipePurchaseModel(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recipe_purchases",
    )
    recipe = models.ForeignKey(
        "app.RecipeModel",
        on_delete=models.CASCADE,
        related_name="purchases",
    )
    payment = models.OneToOneField(
        "app.PaymentModel",
        on_delete=models.CASCADE,
        related_name="recipe_purchase",
    )
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "recipe_purchases"
        ordering = ["-purchased_at"]
        verbose_name = "Recipe purchase"
        verbose_name_plural = "Recipe purchases"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_user_recipe_purchase",
            )
        ]

    def __str__(self) -> str:
        return f"Recipe purchase {self.recipe_id} by user {self.user_id}"
