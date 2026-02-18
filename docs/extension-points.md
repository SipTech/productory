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
