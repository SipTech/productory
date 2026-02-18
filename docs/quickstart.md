![Productory E-commerce](assets/branding/productory-logo-primary-light.png)

# Quickstart

## Local

```bash
make install-dev
make demo-migrate
make demo-run
```

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

Get token:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'
```
