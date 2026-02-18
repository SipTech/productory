from __future__ import annotations

from rest_framework.permissions import SAFE_METHODS, BasePermission

from productory_core.scopes import parse_scopes


class IsStaffOrReadOnly(BasePermission):
    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class HasProductoryScope(BasePermission):
    required_scope = ""

    def has_permission(self, request, view) -> bool:
        if not self.required_scope:
            return True
        auth = request.auth
        scope_value = ""
        if isinstance(auth, dict):
            scope_value = auth.get("scope", "")
        elif hasattr(auth, "get"):
            scope_value = auth.get("scope", "")
        return self.required_scope in parse_scopes(scope_value)
