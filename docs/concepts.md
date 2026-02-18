# Concepts

## Catalog

Catalog keeps product primitives reusable and stable:
- categories
- collections
- products (SKU + money fields)
- stock records

## Checkout

Checkout owns mutable cart state and immutable order snapshots:
- `Cart` + `CartItem`
- `Order` + `OrderItem`
- price snapshots at checkout
- explicit status transitions

## Promotions

Promotions are optional and decoupled from checkout:
- bundles
- promotions
- price resolution service (best single discount rule)

## Services-first architecture

Business logic sits in service modules, not serializers/views:
- `productory_checkout.services`
- `productory_promotions.services`
- `productory_core.store` (currency, timezone, VAT policy from DB config)

This keeps API and admin layers thin.
