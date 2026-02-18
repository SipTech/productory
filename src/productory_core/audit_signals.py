from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

from django.apps import apps
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_save
from django.dispatch import receiver

from productory_core.audit_context import get_current_actor
from productory_core.models import AuditEvent

_EXCLUDED_FIELDS = {"created_at", "updated_at"}
_TRACKED_MODEL_LABELS = {
    "productory_core.Currency",
    "productory_core.TaxRate",
    "productory_core.StoreConfig",
    "productory_checkout.Order",
    "productory_catalog.StockRecord",
    "productory_promotions.Bundle",
    "productory_promotions.Promotion",
}


def _serialize(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    return value


def _model_label(instance) -> str:
    return f"{instance._meta.app_label}.{instance.__class__.__name__}"


def _is_historical_instance(instance) -> bool:
    return instance.__class__.__module__.startswith("__fake__")


def _snapshot(instance) -> dict:
    data: dict = {}
    for field in instance._meta.concrete_fields:
        key = field.attname
        if key in _EXCLUDED_FIELDS:
            continue
        data[key] = _serialize(getattr(instance, key))
    return data


def _record_event(*, instance, action: str, changes: dict) -> None:
    if _is_historical_instance(instance):
        return
    if _model_label(instance) not in _TRACKED_MODEL_LABELS:
        return
    actor = get_current_actor()
    AuditEvent.objects.create(
        model_label=_model_label(instance),
        object_pk=str(instance.pk),
        action=action,
        actor=actor,
        actor_display=(getattr(actor, "get_username", lambda: "")() if actor else ""),
        changes=changes,
    )


@receiver(pre_save)
def capture_before_update(sender, instance, **kwargs):
    if _is_historical_instance(instance):
        return
    if _model_label(instance) not in _TRACKED_MODEL_LABELS:
        return
    if not instance.pk:
        instance._audit_before = None
        return
    previous = sender.objects.filter(pk=instance.pk).first()
    instance._audit_before = _snapshot(previous) if previous else None


@receiver(post_save)
def audit_create_update(sender, instance, created, **kwargs):
    if _is_historical_instance(instance):
        return
    if _model_label(instance) not in _TRACKED_MODEL_LABELS:
        return
    after = _snapshot(instance)
    if created:
        _record_event(
            instance=instance,
            action="created",
            changes={"after": after},
        )
        return

    before = getattr(instance, "_audit_before", None) or {}
    changed = {
        key: {"before": before.get(key), "after": after.get(key)}
        for key in sorted(after.keys())
        if before.get(key) != after.get(key)
    }
    if changed:
        _record_event(instance=instance, action="updated", changes=changed)


@receiver(post_delete)
def audit_delete(sender, instance, **kwargs):
    if _is_historical_instance(instance):
        return
    if _model_label(instance) not in _TRACKED_MODEL_LABELS:
        return
    _record_event(
        instance=instance,
        action="deleted",
        changes={"before": _snapshot(instance)},
    )


@receiver(post_save, sender=apps.get_model("productory_promotions", "BundleItem"))
def audit_bundle_items_change(sender, instance, created, **kwargs):
    _record_event(
        instance=instance.bundle,
        action="relation_updated",
        changes={
            "items": {
                "operation": "add_or_update" if created else "update",
                "bundle_item_id": instance.id,
                "product_id": instance.product_id,
                "quantity": instance.quantity,
            }
        },
    )


@receiver(post_delete, sender=apps.get_model("productory_promotions", "BundleItem"))
def audit_bundle_items_delete(sender, instance, **kwargs):
    _record_event(
        instance=instance.bundle,
        action="relation_updated",
        changes={
            "items": {
                "operation": "remove",
                "product_id": instance.product_id,
            }
        },
    )


@receiver(m2m_changed, sender=apps.get_model("productory_promotions", "Promotion").products.through)
def audit_promotion_products_change(sender, instance, action, pk_set, **kwargs):
    if action not in {"post_add", "post_remove", "post_clear"}:
        return
    _record_event(
        instance=instance,
        action="relation_updated",
        changes={"products": {"operation": action, "product_ids": sorted(pk_set or [])}},
    )


@receiver(m2m_changed, sender=apps.get_model("productory_promotions", "Promotion").bundles.through)
def audit_promotion_bundles_change(sender, instance, action, pk_set, **kwargs):
    if action not in {"post_add", "post_remove", "post_clear"}:
        return
    _record_event(
        instance=instance,
        action="relation_updated",
        changes={"bundles": {"operation": action, "bundle_ids": sorted(pk_set or [])}},
    )
