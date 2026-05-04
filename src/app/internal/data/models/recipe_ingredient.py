from django.db import models


class RecipeIngredientModel(models.Model):
    recipe = models.ForeignKey(
        "app.RecipeModel",
        on_delete=models.CASCADE,
        related_name="ingredients",
    )
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "recipe_ingredients"
        ordering = ["id"]
        verbose_name = "Recipe ingredient"
        verbose_name_plural = "Recipe ingredients"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "name"],
                name="unique_recipe_ingredient_name",
            )
        ]

    def __str__(self) -> str:
        return self.name
