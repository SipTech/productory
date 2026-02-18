# Contributing

## Setup

```bash
make install-dev
make demo-migrate
```

## Run checks

```bash
make qa
make coverage
```

## Pull requests

- Add or adjust tests for behavior changes.
- Keep business logic in services.
- Keep serializers focused on validation and transformation.
- Use `make` targets in docs and examples for consistency.
