from __future__ import annotations

from types import SimpleNamespace

from productory_core.conf import get_setting
from productory_core.permissions import HasProductoryScope, IsStaffOrReadOnly
from productory_core.scopes import parse_scopes


class ScopePermission(HasProductoryScope):
    required_scope = "order:manage"


def test_get_setting_reads_defaults(settings):
    settings.PRODUCTORY = {}
    assert get_setting("DEFAULT_CURRENCY") == "ZAR"


def test_parse_scopes_handles_blank_values():
    assert parse_scopes(None) == set()
    assert parse_scopes("catalog:read order:manage") == {"catalog:read", "order:manage"}


def test_scope_permission():
    permission = ScopePermission()
    request = SimpleNamespace(auth={"scope": "catalog:read order:manage"})
    assert permission.has_permission(request, view=None)


def test_staff_or_read_only_permission():
    permission = IsStaffOrReadOnly()
    get_request = SimpleNamespace(
        method="GET", user=SimpleNamespace(is_authenticated=False, is_staff=False)
    )
    assert permission.has_permission(get_request, view=None)

    post_request = SimpleNamespace(
        method="POST", user=SimpleNamespace(is_authenticated=True, is_staff=True)
    )
    assert permission.has_permission(post_request, view=None)
