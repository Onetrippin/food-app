from django.db import models


class RecipeModel(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "recipes"
        ordering = ["-created_at"]
        verbose_name = "Recipe"
        verbose_name_plural = "Recipes"

    def __str__(self) -> str:
        return self.title
