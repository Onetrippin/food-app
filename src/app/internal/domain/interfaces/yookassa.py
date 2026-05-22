from __future__ import annotations

from typing import Protocol


class YooKassaProviderInterface(Protocol):
    def create_payment(
        self,
        amount_value: str,
        currency: str,
        description: str,
        return_url: str,
        metadata: dict[str, str],
        save_payment_method: bool = False,
    ) -> dict[str, object]:
        ...
