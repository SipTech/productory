# Extension Points

## Signals and webhooks

Productory emits integration hooks:
- `productory_core.hooks.order_created`
- `productory_core.hooks.order_status_changed`

Enable outbound webhooks through settings:

```python
PRODUCTORY = {
    "ENABLE_WEBHOOKS": True,
    "WEBHOOK_URL": "https://example.com/hooks/productory",
}
```

## Permissions/scopes

Use `productory_core.permissions` and `productory_core.scopes` to enforce API scopes in host projects.

## Pricing rules

To customize discount behavior, extend `productory_promotions.services.resolve_cart_pricing` and call it from your checkout flow.

## Store configuration

Base currency, timezone, VAT rate, and VAT-inclusive/exclusive mode are stored in DB (`Currency`, `TaxRate`, `Store configuration` in admin).
You can replace `productory_core.store.get_store_pricing_policy` in host-level service orchestration if you need tenant-specific behavior.
