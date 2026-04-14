from __future__ import annotations

import hashlib
from datetime import datetime

from django.db import transaction
from django.utils import timezone

from app.internal.data.models import PasswordChangeCodeModel


class DjangoPasswordChangeCodeRepository:
    def invalidate_for_user(self, user_id: int) -> None:
        PasswordChangeCodeModel.objects.filter(user_id=user_id, used_at__isnull=True).update(
            used_at=timezone.now()
        )

    def create(self, user_id: int, code: str, expires_at: datetime) -> None:
        PasswordChangeCodeModel.objects.create(
            user_id=user_id,
            code_hash=self._hash_code(code),
            expires_at=expires_at,
        )

    @transaction.atomic
    def consume(self, user_id: int, code: str) -> bool:
        password_change_code = (
            PasswordChangeCodeModel.objects.select_for_update()
            .filter(
                user_id=user_id,
                code_hash=self._hash_code(code),
                used_at__isnull=True,
                expires_at__gt=timezone.now(),
            )
            .order_by("-created_at")
            .first()
        )

        if password_change_code is None:
            return False

        password_change_code.used_at = timezone.now()
        password_change_code.save(update_fields=["used_at"])
        return True

    @staticmethod
    def _hash_code(code: str) -> str:
        return hashlib.sha256(code.encode("utf-8")).hexdigest()
