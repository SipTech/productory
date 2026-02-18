![Productory E-commerce](assets/branding/productory-logo-flat-light.png)

# API Examples

## Start demo

```bash
make install-dev
make demo-run
make loaddata
```

Default base URL:

```bash
export BASE_URL=http://127.0.0.1:8010
```

## Create category

```bash
curl -X POST "$BASE_URL/api/catalog/categories/" \
  -H "Content-Type: application/json" \
  -d '{"name":"Coffee","slug":"coffee","description":"Beans"}'
```

## Create product

```bash
curl -X POST "$BASE_URL/api/catalog/products/" \
  -H "Content-Type: application/json" \
  -d '{"name":"Single Origin","slug":"single-origin","sku":"COF-001","category_id":1,"price_amount":"12.50","currency":"ZAR","is_active":true}'
```

## Create cart + add item

```bash
curl -X POST "$BASE_URL/api/checkout/carts/" \
  -H "Content-Type: application/json" \
  -d '{"email":"buyer@example.com"}'

curl -X POST "$BASE_URL/api/checkout/cart-items/" \
  -H "Content-Type: application/json" \
  -d '{"cart_id":1,"product_id":1,"quantity":2}'
```

## Checkout cart

```bash
curl -X POST "$BASE_URL/api/checkout/checkout/" \
  -H "Content-Type: application/json" \
  -d '{"cart_id":1,"email":"buyer@example.com","full_name":"Buyer"}'
```

Response includes both VAT-inclusive and VAT-exclusive totals:
- `subtotal_excl_vat_amount`
- `subtotal_incl_vat_amount`
- `total_excl_vat_amount`
- `total_incl_vat_amount`
- `tax_amount`

## Transition order status

```bash
curl -X POST "$BASE_URL/api/checkout/orders/1/transition/" \
  -H "Content-Type: application/json" \
  -d '{"status":"paid"}'
```

## Inspect URLs quickly

```bash
make show-urls
```

## Internal dashboard KPIs (staff only)

```bash
curl -X GET "$BASE_URL/api/internal/dashboard/kpis/?date_from=2026-02-01&date_to=2026-02-18" \
  -u admin:admin
```
