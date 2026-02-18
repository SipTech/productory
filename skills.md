# Productory Contributor + Agent Guide

This document is the project working contract for human contributors and AI agents.

## 1) Current Project Shape

- Productory is a reusable Django package-first project.
- Core source: `src/`
- Demo project: `demo/`
- Tests: `tests/`
- Docs and diagrams: `docs/`

Primary Django apps:

- `productory_core`
- `productory_catalog`
- `productory_checkout`
- `productory_promotions`
- `productory_ecommerce` (URL gateway)

## 2) Architecture Rules

- Keep business logic in services, not views/serializers.
- Serializers validate and transform data only.
- Views orchestrate HTTP concerns only.
- Pricing and totals logic must stay in service layer:
  - `productory_checkout.services`
  - `productory_promotions.services`
  - `productory_core.store`
- Internal analytics/KPI logic belongs in `productory_core.services.dashboard_kpis`.

## 3) Money, VAT, and Snapshots

- Never use floating-point fields for money.
- Use `DecimalField(max_digits=10, decimal_places=2)` for money amounts.
- `OrderItem` must preserve purchase-time snapshots (`unit_price_snapshot`, `line_total`).
- Recompute cart totals through service logic before checkout.
- Respect store pricing policy from DB config (`Currency`, `TaxRate`, `StoreConfig`).

## 4) API and Permission Conventions

- Public API gateway is mounted through `productory_ecommerce.urls`:
  - `catalog/`, `checkout/`, `promotions/`, `internal/`
- Internal KPI endpoint is staff-only:
  - `/api/internal/dashboard/kpis/`
  - permission: `IsAdminUser`
- Prefer explicit permissions over implicit defaults.

## 5) Audit Trail Rules (v0.2+)

- Audit events are stored in `productory_core.AuditEvent`.
- Required audit outcomes:
  - what changed (`changes` JSON; before/after or relation operations)
  - who changed it (`actor` / `actor_display` when authenticated)
  - when (`created_at`)
- Tracked models:
  - `Currency`, `TaxRate`, `StoreConfig`
  - `Order`
  - `StockRecord`
  - `Bundle`, `Promotion`
- Use signal-based tracking; avoid audit writes in business logic call sites.
- Keep migration safety in mind: do not write audit rows for historical (`__fake__`) model instances.

## 6) Admin and UX Conventions

- Preserve existing Productory brand language for Django admin.
- `demo/templates/admin/base_site.html` is the branding base.
- Login page customization lives in `demo/templates/admin/login.html`.
- Internal dashboard (`demo/templates/admin/index.html`) must keep KPI cards/charts functional.

## 7) Testing Expectations

- Add/maintain tests when changing behavior.
- Minimum checks before commit:
  - `python3 -m ruff check src tests demo`
  - `python3 -m mypy src`
  - `python3 -m pytest tests -q`
- Docker smoke path should remain green:
  - `make test`
- Keep coverage floor aligned with project config (currently 80% gate).

## 8) Docs + Diagrams Update Policy

Whenever implementation changes affect domain structure or behavior:

- Update `README.md` (features, behavior, setup impact).
- Update ERD sources:
  - `docs/productory-ecommerce-erd.mmd`
  - `docs/productory-ecommerce.erd`
- Update architecture flow if routing/dependencies changed:
  - `docs/productory-ecommerce.mmd`
- Keep non-technical explanations readable in README.

## 9) Release and Versioning

- Follow semantic versioning.
- While in `0.x`, breaking changes require a minor bump.
- For release commits:
  - bump version in `pyproject.toml`
  - update `CHANGELOG.md`
  - create annotated git tag (for example: `v0.2.0`)
