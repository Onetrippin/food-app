from django.conf import settings
from django.db import models


class PasswordChangeCodeModel(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_change_codes",
    )
    code_hash = models.CharField(max_length=64)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "password_change_codes"
        ordering = ["-created_at"]
        verbose_name = "Password change code"
        verbose_name_plural = "Password change codes"

    def __str__(self) -> str:
        return f"Password change code for user {self.user_id}"
