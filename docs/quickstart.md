![Productory E-commerce](assets/branding/productory-logo-primary-light.png)

# Quickstart

## Local

```bash
make install-dev
make demo-run
```

`make demo-run` runs the demo stack in detached Docker mode and applies migrations.
It seeds 10 categories, 10 collections, 50 products, stock, 6 bundles, and 5 month-end promotions.
It also seeds 10 addresses, 32 varied carts, and 18 varied orders for dashboard demos.
It also seeds store defaults in DB: `ZAR`, `Africa/Johannesburg`, VAT `15%` (prices VAT-inclusive).
The Django admin dashboard is branded and theme-aware (light/dark toggle).
Create an admin account before using admin or staff-only KPI endpoints:

```bash
make superuser
```

```bash
make demo-logs
make demo-stop
make loaddata
```

## Store pricing configuration

Open Django admin and configure:
- `Currency`
- `TaxRate`
- `Store configuration`

All new carts/products/bundles and checkout VAT calculations follow this DB config.

## Validate

```bash
make qa
make coverage
```

## Docker

```bash
make up
make migrations
make loaddata
```

If you need custom values, copy `.env.example` to `.env` and run with `make ENV_FILE=.env up`.

## Optional JWT in demo

```bash
export DEMO_ENABLE_JWT=true
make demo-run
```

Get token (use the superuser credentials you created):

```bash
curl -X POST http://127.0.0.1:8010/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "<your-superuser-username>", "password": "<your-superuser-password>"}'
```
