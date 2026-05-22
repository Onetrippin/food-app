from __future__ import annotations

import uuid

import requests
from django.conf import settings


class YooKassaProvider:
    def create_payment(
        self,
        amount_value: str,
        currency: str,
        description: str,
        return_url: str,
        metadata: dict[str, str],
        save_payment_method: bool = False,
    ) -> dict[str, object]:
        if not settings.YOOKASSA_SHOP_ID or not settings.YOOKASSA_SECRET_KEY:
            raise ValueError("YooKassa credentials are not configured.")

        try:
            response = requests.post(
                "https://api.yookassa.ru/v3/payments",
                auth=(settings.YOOKASSA_SHOP_ID, settings.YOOKASSA_SECRET_KEY),
                headers={
                    "Idempotence-Key": str(uuid.uuid4()),
                    "Content-Type": "application/json",
                },
                json={
                    "amount": {
                        "value": amount_value,
                        "currency": currency,
                    },
                    "capture": True,
                    "confirmation": {
                        "type": "redirect",
                        "return_url": return_url,
                    },
                    "description": description,
                    "metadata": metadata,
                    "save_payment_method": save_payment_method,
                },
                timeout=30,
            )
            response.raise_for_status()
        except requests.RequestException as error:
            raise ValueError("Failed to create YooKassa payment.") from error

        return response.json()
