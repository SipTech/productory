from __future__ import annotations

import re
from textwrap import wrap

from django.core.management.base import BaseCommand
from django.urls import URLPattern, URLResolver, get_resolver
from rest_framework.permissions import AllowAny
from rest_framework.settings import api_settings
from rest_framework.views import APIView

_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"
_GREEN = "\033[32m"
_RED = "\033[31m"
_CYAN = "\033[36m"
_YELLOW = "\033[33m"
_MAGENTA = "\033[35m"
_METHOD_COLORS = {
    "GET": "\033[34m",
    "POST": "\033[32m",
    "PUT": "\033[33m",
    "PATCH": "\033[35m",
    "DELETE": "\033[31m",
    "OPTIONS": "\033[36m",
    "HEAD": "\033[90m",
    "ANY": "\033[37m",
}
_ANSI_RE = re.compile(r"\x1B\[[0-9;]*m")
_PATH_VAR_RE = re.compile(r"<[^>]+>")
_REGEX_GROUP_RE = re.compile(r"\(\?P<[^>]+>[^)]*\)")
_REGEX_CLASS_RE = re.compile(r"\[[^\]]+\]")


class Command(BaseCommand):
    help = "Print resolved URL patterns in a colorized table with auth/security details."

    def handle(self, *args, **options):
        resolver = get_resolver()
        rows = self._walk(resolver.url_patterns)
        self._render_table(rows)

    def _walk(self, patterns, prefix: str = "") -> list[tuple[str, str, str, str, str]]:
        lines: list[tuple[str, str, str, str, str]] = []
        for pattern in patterns:
            if isinstance(pattern, URLPattern):
                route = prefix + str(pattern.pattern)
                lines.extend(self._rows_for_pattern(route, pattern.callback))
            elif isinstance(pattern, URLResolver):
                nested_prefix = prefix + str(pattern.pattern)
                lines.extend(self._walk(pattern.url_patterns, nested_prefix))
        return lines

    def _rows_for_pattern(self, route: str, callback) -> list[tuple[str, str, str, str, str]]:
        domain = self._domain(route)
        uri = self._normalize_uri(route)
        view_cls = getattr(callback, "cls", None)

        if view_cls and issubclass(view_cls, APIView):
            security = self._security_details(route, view_cls)
            method_actions = getattr(callback, "actions", None) or {}
            rows: list[tuple[str, str, str, str, str]] = []
            if method_actions:
                for method, action in sorted(method_actions.items()):
                    rows.append((domain, method.upper(), uri, action, security))
                return rows

            explicit_methods = [
                m for m in ("get", "post", "put", "patch", "delete") if m in view_cls.__dict__
            ]
            if explicit_methods:
                for method in explicit_methods:
                    rows.append((domain, method.upper(), uri, method, security))
                return rows

            return [(domain, "ANY", uri, view_cls.__name__, security)]

        security = self._security_details(route, None)
        action = getattr(callback, "__name__", "view")
        return [(domain, "ANY", uri, action, security)]

    def _domain(self, route: str) -> str:
        if route.startswith("api/"):
            parts = route.split("/")
            if len(parts) > 1 and parts[1]:
                return parts[1]
            return "api"
        if route.startswith("admin/"):
            return "admin"
        return "root"

    @staticmethod
    def _normalize_uri(route: str) -> str:
        normalized = route
        if normalized.startswith("^"):
            normalized = normalized[1:]
        if normalized.endswith("$"):
            normalized = normalized[:-1]
        return normalized

    def _security_details(self, route: str, view_cls) -> str:
        if route.startswith("admin/login/"):
            return "PUBLIC | Django admin login"
        if route.startswith("admin/"):
            return "AUTH_REQUIRED | Django admin session auth + CSRF"

        if view_cls and issubclass(view_cls, APIView):
            permission_classes = getattr(view_cls, "permission_classes", None)
            if permission_classes is None:
                permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES
            authentication_classes = getattr(view_cls, "authentication_classes", None)
            if authentication_classes is None:
                authentication_classes = api_settings.DEFAULT_AUTHENTICATION_CLASSES

            permission_names = ",".join(
                self._permission_type(p).__name__ for p in permission_classes or []
            )
            auth_names = ",".join(
                self._permission_type(a).__name__ for a in authentication_classes or []
            )
            access = (
                "PUBLIC"
                if permission_classes is not None
                and all(self._is_allow_any(permission) for permission in permission_classes)
                else "AUTH_REQUIRED"
            )
            return f"{access} | perms={permission_names or 'None'} | auth={auth_names or 'None'}"

        return "AUTH_REQUIRED | Unknown/non-DRF route"

    @staticmethod
    def _permission_type(permission):
        return permission if isinstance(permission, type) else permission.__class__

    def _is_allow_any(self, permission) -> bool:
        permission_type = self._permission_type(permission)
        return issubclass(permission_type, AllowAny)

    def _render_table(self, rows: list[tuple[str, str, str, str, str]]) -> None:
        rows = sorted(rows, key=lambda r: (r[0], r[2], r[1], r[3]))
        headers = ("Domain", "Method", "URI", "Action", "Middleware (security)")
        domain_w = min(12, max(len(headers[0]), *(len(r[0]) for r in rows)))
        method_w = min(7, max(len(headers[1]), *(len(r[1]) for r in rows)))
        uri_w = min(104, max(len(headers[2]), *(len(r[2]) for r in rows)))
        action_w = min(20, max(len(headers[3]), *(len(r[3]) for r in rows)))
        security_w = min(58, max(len(headers[4]), *(len(r[4]) for r in rows)))

        border = (
            f"+{'-' * (domain_w + 2)}+{'-' * (method_w + 2)}+{'-' * (uri_w + 2)}+"
            f"{'-' * (action_w + 2)}+{'-' * (security_w + 2)}+"
        )
        header = (
            f"| {self._pad_ansi(_BOLD + headers[0] + _RESET, domain_w)}"
            f" | {self._pad_ansi(_BOLD + headers[1] + _RESET, method_w)}"
            f" | {self._pad_ansi(_BOLD + headers[2] + _RESET, uri_w)}"
            f" | {self._pad_ansi(_BOLD + headers[3] + _RESET, action_w)}"
            f" | {self._pad_ansi(_BOLD + headers[4] + _RESET, security_w)} |"
        )

        self.stdout.write(border)
        self.stdout.write(header)
        self.stdout.write(border)
        for domain, method, uri, action, security in rows:
            security_lines = wrap(security, width=security_w) or [""]
            row_height = len(security_lines)
            for i in range(row_height):
                d = domain if i == 0 else ""
                m = self._color_method(method) if i == 0 else ""
                u = self._color_uri(uri) if i == 0 else ""
                a = action if i == 0 else ""
                s = self._color_security(security_lines[i])
                self.stdout.write(
                    f"| {self._pad_ansi(d, domain_w)}"
                    f" | {self._pad_ansi(m, method_w)}"
                    f" | {self._pad_ansi(u, uri_w)}"
                    f" | {self._pad_ansi(a, action_w)}"
                    f" | {self._pad_ansi(s, security_w)} |"
                )
            self.stdout.write(border)

    def _color_method(self, method: str) -> str:
        color = _METHOD_COLORS.get(method, _METHOD_COLORS["ANY"])
        return f"{color}{method}{_RESET}"

    def _color_uri(self, uri: str) -> str:
        highlighted = uri
        highlighted = _REGEX_GROUP_RE.sub(lambda m: f"{_MAGENTA}{m.group(0)}{_RESET}", highlighted)
        highlighted = _REGEX_CLASS_RE.sub(lambda m: f"{_CYAN}{m.group(0)}{_RESET}", highlighted)
        highlighted = _PATH_VAR_RE.sub(lambda m: f"{_YELLOW}{m.group(0)}{_RESET}", highlighted)
        return highlighted

    @staticmethod
    def _color_security(text: str) -> str:
        if text.startswith("PUBLIC"):
            return text.replace("PUBLIC", f"{_GREEN}PUBLIC{_RESET}", 1)
        if text.startswith("AUTH_REQUIRED"):
            return text.replace("AUTH_REQUIRED", f"{_RED}AUTH_REQUIRED{_RESET}", 1)
        return text

    @staticmethod
    def _visible_len(value: str) -> int:
        return len(_ANSI_RE.sub("", value))

    def _pad_ansi(self, value: str, width: int) -> str:
        visible = self._visible_len(value)
        if visible >= width:
            return value
        return value + (" " * (width - visible))
