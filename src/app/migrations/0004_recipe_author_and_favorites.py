from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("app", "0003_recipe_ingredient"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipemodel",
            name="author",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="recipes",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.CreateModel(
            name="RecipeFavoriteModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="favorited_by_users",
                        to="app.recipemodel",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="favorite_recipes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "recipe_favorites",
                "ordering": ["-created_at"],
                "verbose_name": "Recipe favorite",
                "verbose_name_plural": "Recipe favorites",
            },
        ),
        migrations.AddConstraint(
            model_name="recipefavoritemodel",
            constraint=models.UniqueConstraint(
                fields=("user", "recipe"),
                name="unique_user_recipe_favorite",
            ),
        ),
    ]
