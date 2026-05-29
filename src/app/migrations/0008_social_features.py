from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("app", "0007_monetization"),
    ]

    operations = [
        migrations.CreateModel(
            name="AuthorFollowModel",
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
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="followers",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "subscriber",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="author_follows",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "author_follows",
                "ordering": ["-created_at"],
                "verbose_name": "Author follow",
                "verbose_name_plural": "Author follows",
            },
        ),
        migrations.CreateModel(
            name="NotificationModel",
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
                (
                    "notification_type",
                    models.CharField(
                        choices=[("recipe_published", "Recipe published")],
                        max_length=32,
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("message", models.TextField()),
                ("is_read", models.BooleanField(default=False)),
                ("read_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "recipe",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to="app.recipemodel",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "notifications",
                "ordering": ["-created_at"],
                "verbose_name": "Notification",
                "verbose_name_plural": "Notifications",
            },
        ),
        migrations.CreateModel(
            name="RecipeReportModel",
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
                ("reason", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("reviewed", "Reviewed"),
                            ("rejected", "Rejected"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reports",
                        to="app.recipemodel",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recipe_reports",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "recipe_reports",
                "ordering": ["-created_at"],
                "verbose_name": "Recipe report",
                "verbose_name_plural": "Recipe reports",
            },
        ),
        migrations.CreateModel(
            name="RecipeReviewModel",
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
                (
                    "rating",
                    models.PositiveSmallIntegerField(
                        validators=[MinValueValidator(1), MaxValueValidator(5)]
                    ),
                ),
                ("review_text", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="app.recipemodel",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recipe_reviews",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "recipe_reviews",
                "ordering": ["-updated_at"],
                "verbose_name": "Recipe review",
                "verbose_name_plural": "Recipe reviews",
            },
        ),
        migrations.AddConstraint(
            model_name="authorfollowmodel",
            constraint=models.UniqueConstraint(
                fields=("subscriber", "author"),
                name="unique_subscriber_author_follow",
            ),
        ),
        migrations.AddConstraint(
            model_name="recipereviewmodel",
            constraint=models.UniqueConstraint(
                fields=("user", "recipe"),
                name="unique_user_recipe_review",
            ),
        ),
    ]
