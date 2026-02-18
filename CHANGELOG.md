# Changelog

## Unreleased

- Initial OSS scaffold for installable Django ecommerce apps.
- Added modular apps: `productory_core`, `productory_catalog`, `productory_checkout`, `productory_promotions`.
- Added bundle/promotion pricing resolution and checkout status transitions.
- Added admin CSV exports and integration hooks (signals + optional webhooks).
- Added demo JWT support toggle, release workflow, community templates, and expanded docs.
- Added factory-based tests, mypy checks, ruff format checks, and 80% coverage gate.
- Removed legacy monolith code and moved fully to `src/` package + `demo/` workflow.
- Replaced old MySQL/docker bootstrap with rewrite-aligned Postgres docker stack and `make`-driven commands.
