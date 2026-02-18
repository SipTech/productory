![Productory E-commerce](assets/branding/productory-logo-flat-light.png)

# API Examples

## Start demo

```bash
make install-dev
make demo-migrate
make demo-run
```

## Create category

```bash
curl -X POST http://127.0.0.1:8000/api/catalog/categories/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Coffee","slug":"coffee","description":"Beans"}'
```

## Create product

```bash
curl -X POST http://127.0.0.1:8000/api/catalog/products/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Single Origin","slug":"single-origin","sku":"COF-001","category_id":1,"price_amount":"12.50","currency":"USD","is_active":true}'
```

## Create cart + add item

```bash
curl -X POST http://127.0.0.1:8000/api/checkout/carts/ \
  -H "Content-Type: application/json" \
  -d '{"email":"buyer@example.com","currency":"USD"}'

curl -X POST http://127.0.0.1:8000/api/checkout/cart-items/ \
  -H "Content-Type: application/json" \
  -d '{"cart_id":1,"product_id":1,"quantity":2}'
```

## Checkout cart

```bash
curl -X POST http://127.0.0.1:8000/api/checkout/checkout/ \
  -H "Content-Type: application/json" \
  -d '{"cart_id":1,"email":"buyer@example.com","full_name":"Buyer"}'
```

## Transition order status

```bash
curl -X POST http://127.0.0.1:8000/api/checkout/orders/1/transition/ \
  -H "Content-Type: application/json" \
  -d '{"status":"paid"}'
```

## Inspect URLs quickly

```bash
make show-urls
```
