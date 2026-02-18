# Changelog

## Unreleased

## 0.2.0 - 2026-02-18

- Added a signal-based audit trail (`AuditEvent`) for `Currency`, `TaxRate`, `StoreConfig`,
  `Order`, `StockRecord`, `Bundle`, and `Promotion` with `what/who/when` history.
- Added audit actor capture middleware and admin read-only audit viewer.
- Added audit coverage tests and migration-safe signal handling for historical migration models.
- Added a color-coded tabular `show_urls` command output including domain, method, URI,
  action, and security/auth details.
- Updated demo/admin experience with branded login page theming and improved favicon behavior.
- Expanded README and ERD docs (including plain-English ERD legend and audit model relationships).
- Updated demo container build to include dev dependencies so `make test` works in Docker.

- Initial OSS scaffold for installable Django ecommerce apps.
- Added modular apps: `productory_core`, `productory_catalog`, `productory_checkout`, `productory_promotions`.
- Added bundle/promotion pricing resolution and checkout status transitions.
- Added admin CSV exports and integration hooks (signals + optional webhooks).
- Added demo JWT support toggle, release workflow, community templates, and expanded docs.
- Added factory-based tests, mypy checks, ruff format checks, and 80% coverage gate.
- Removed legacy monolith code and moved fully to `src/` package + `demo/` workflow.
- Replaced old MySQL/docker bootstrap with rewrite-aligned Postgres docker stack and `make`-driven commands.
