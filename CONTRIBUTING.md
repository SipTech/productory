# Contributing

## Setup

```bash
make install-dev
make demo-migrate
```

If you want local overrides:

```bash
cp .env.example .env
make ENV_FILE=.env up
```

## Run checks

```bash
make qa
make coverage
```

## Branches and commits

- Branch from `main` using `feature/<short-name>` or `fix/<short-name>`.
- Keep commits focused and descriptive (imperative style).
- Include tests in the same PR as behavior changes.

## Testing paths

- Fast smoke tests in Docker:
  - `make test`
- Full test suite in Docker:
  - `make test-all`
- One test target:
  - `make test-one TEST=tests/test_api.py::test_catalog_and_checkout_flow`

## Architecture expectations

- Keep domain/business logic in service modules.
- Keep views/viewsets thin.
- Keep serializers focused on validation and representation.
- Add migrations only for intentional schema changes.

## Adding a new app/module

- Create app code under `src/`.
- Register the app in demo settings if demo exposure is required.
- Mount routes from `productory_ecommerce.urls` when API surface changes.
- Add tests in `tests/` for service and API behavior.
- Update diagrams/docs in `docs/` if models or flows change.

## Release notes

- Update `CHANGELOG.md` for user-visible changes.
- Tag releases using semantic versioning (`vMAJOR.MINOR.PATCH`).
- Keep `pyproject.toml` metadata and README links in sync with the repo.

## Pull requests

- Add or adjust tests for behavior changes.
- Describe behavior changes, migrations, and rollback considerations.
- Use `make` targets in docs and examples for consistency.
