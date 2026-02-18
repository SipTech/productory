from __future__ import annotations

from productory_core.hooks import emit_webhook_event


def test_emit_webhook_event_noop_when_disabled(settings):
    settings.PRODUCTORY = {"ENABLE_WEBHOOKS": False, "WEBHOOK_URL": "https://example.com"}
    emit_webhook_event("order.created", {"id": 1})


def test_emit_webhook_event_noop_without_url(settings):
    settings.PRODUCTORY = {"ENABLE_WEBHOOKS": True, "WEBHOOK_URL": ""}
    emit_webhook_event("order.created", {"id": 1})
