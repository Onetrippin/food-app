from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("app", "0006_author_application"),
    ]

    operations = [
        migrations.AddField(
            model_name="authorapplicationmodel",
            name="is_subscription_enabled",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="authorapplicationmodel",
            name="subscription_currency",
            field=models.CharField(default="RUB", max_length=3),
        ),
        migrations.AddField(
            model_name="authorapplicationmodel",
            name="subscription_price",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=10,
                validators=[MinValueValidator(0)],
            ),
        ),
        migrations.AddField(
            model_name="recipemodel",
            name="price_amount",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=10,
                validators=[MinValueValidator(0)],
            ),
        ),
        migrations.AddField(
            model_name="recipemodel",
            name="price_currency",
            field=models.CharField(default="RUB", max_length=3),
        ),
        migrations.CreateModel(
            name="PaymentModel",
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
                    "payment_type",
                    models.CharField(
                        choices=[
                            ("recipe_purchase", "Recipe purchase"),
                            ("author_subscription", "Author subscription"),
                        ],
                        max_length=32,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("succeeded", "Succeeded"),
                            ("canceled", "Canceled"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[MinValueValidator(0)],
                    ),
                ),
                ("currency", models.CharField(default="RUB", max_length=3)),
                ("description", models.CharField(max_length=255)),
                ("yookassa_payment_id", models.CharField(max_length=128, unique=True)),
                ("confirmation_url", models.URLField(blank=True)),
                ("payment_method_id", models.CharField(blank=True, max_length=128)),
                ("save_payment_method", models.BooleanField(default=False)),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "author",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="author_subscription_payments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "recipe",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payments",
                        to="app.recipemodel",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "payments",
                "ordering": ["-created_at"],
                "verbose_name": "Payment",
                "verbose_name_plural": "Payments",
            },
        ),
        migrations.CreateModel(
            name="AuthorSubscriptionModel",
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
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[MinValueValidator(0)],
                    ),
                ),
                ("currency", models.CharField(default="RUB", max_length=3)),
                ("payment_method_id", models.CharField(blank=True, max_length=128)),
                ("started_at", models.DateTimeField()),
                ("expires_at", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subscribers",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "subscriber",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="author_subscriptions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "author_subscriptions",
                "ordering": ["-expires_at"],
                "verbose_name": "Author subscription",
                "verbose_name_plural": "Author subscriptions",
            },
        ),
        migrations.CreateModel(
            name="RecipePurchaseModel",
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
                ("purchased_at", models.DateTimeField(auto_now_add=True)),
                (
                    "payment",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recipe_purchase",
                        to="app.paymentmodel",
                    ),
                ),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="purchases",
                        to="app.recipemodel",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recipe_purchases",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "recipe_purchases",
                "ordering": ["-purchased_at"],
                "verbose_name": "Recipe purchase",
                "verbose_name_plural": "Recipe purchases",
            },
        ),
        migrations.AddConstraint(
            model_name="recipepurchasemodel",
            constraint=models.UniqueConstraint(
                fields=("user", "recipe"),
                name="unique_user_recipe_purchase",
            ),
        ),
    ]
