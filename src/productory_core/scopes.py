from __future__ import annotations

CATALOG_READ = "catalog:read"
CATALOG_WRITE = "catalog:write"
CHECKOUT_WRITE = "checkout:write"
ORDER_READ = "order:read"
ORDER_MANAGE = "order:manage"


def parse_scopes(scope_value: str | None) -> set[str]:
    if not scope_value:
        return set()
    return {scope.strip() for scope in scope_value.split() if scope.strip()}
