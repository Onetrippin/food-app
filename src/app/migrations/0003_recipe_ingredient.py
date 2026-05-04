from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0002_password_change_code"),
    ]

    operations = [
        migrations.CreateModel(
            name="RecipeIngredientModel",
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
                ("name", models.CharField(max_length=255)),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ingredients",
                        to="app.recipemodel",
                    ),
                ),
            ],
            options={
                "db_table": "recipe_ingredients",
                "ordering": ["id"],
                "verbose_name": "Recipe ingredient",
                "verbose_name_plural": "Recipe ingredients",
            },
        ),
        migrations.AddConstraint(
            model_name="recipeingredientmodel",
            constraint=models.UniqueConstraint(
                fields=("recipe", "name"),
                name="unique_recipe_ingredient_name",
            ),
        ),
    ]
