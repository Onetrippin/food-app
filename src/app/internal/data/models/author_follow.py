from django.conf import settings
from django.db import models


class AuthorFollowModel(models.Model):
    subscriber = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="author_follows",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followers",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "author_follows"
        ordering = ["-created_at"]
        verbose_name = "Author follow"
        verbose_name_plural = "Author follows"
        constraints = [
            models.UniqueConstraint(
                fields=["subscriber", "author"],
                name="unique_subscriber_author_follow",
            )
        ]

    def __str__(self) -> str:
        return f"Follow author {self.author_id} by user {self.subscriber_id}"
