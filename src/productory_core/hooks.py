from __future__ import annotations

import json
from urllib.request import Request, urlopen

from django.dispatch import Signal

from productory_core.conf import get_setting

order_created = Signal()
order_status_changed = Signal()


def emit_webhook_event(event_name: str, payload: dict) -> None:
    if not get_setting("ENABLE_WEBHOOKS"):
        return

    webhook_url = get_setting("WEBHOOK_URL", "")
    if not webhook_url:
        return

    request = Request(
        webhook_url,
        data=json.dumps({"event": event_name, "payload": payload}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    # Fire-and-forget hook for integrations; failures should not break checkout.
    try:
        with urlopen(request, timeout=3):
            pass
    except Exception:
        return
