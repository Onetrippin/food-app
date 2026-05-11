from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("app", "0004_recipe_author_and_favorites"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipemodel",
            name="is_published",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="recipemodel",
            name="views_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.CreateModel(
            name="RecipeLikeModel",
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
                        related_name="liked_by_users",
                        to="app.recipemodel",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="liked_recipes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "recipe_likes",
                "ordering": ["-created_at"],
                "verbose_name": "Recipe like",
                "verbose_name_plural": "Recipe likes",
            },
        ),
        migrations.AddConstraint(
            model_name="recipelikemodel",
            constraint=models.UniqueConstraint(
                fields=("user", "recipe"),
                name="unique_user_recipe_like",
            ),
        ),
    ]
