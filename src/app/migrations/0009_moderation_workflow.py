from django.db import migrations, models


def seed_moderation_defaults(apps, schema_editor):
    RecipeModel = apps.get_model("app", "RecipeModel")
    RecipeReviewModel = apps.get_model("app", "RecipeReviewModel")

    RecipeModel.objects.filter(is_published=True).update(moderation_status="approved")
    RecipeModel.objects.filter(is_published=False).update(moderation_status="draft")
    RecipeReviewModel.objects.update(moderation_status="approved")


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0008_social_features"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipemodel",
            name="moderation_comment",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="recipemodel",
            name="moderation_status",
            field=models.CharField(
                choices=[
                    ("draft", "Draft"),
                    ("pending", "Pending"),
                    ("approved", "Approved"),
                    ("rejected", "Rejected"),
                ],
                default="draft",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="recipemodel",
            name="reviewed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="recipereportmodel",
            name="moderation_comment",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="recipereportmodel",
            name="reviewed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="recipereviewmodel",
            name="moderation_comment",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="recipereviewmodel",
            name="moderation_status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("approved", "Approved"),
                    ("rejected", "Rejected"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="recipereviewmodel",
            name="reviewed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(seed_moderation_defaults, migrations.RunPython.noop),
    ]
