from __future__ import annotations

from productory_core.audit_context import clear_current_actor, set_current_actor


class AuditActorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_current_actor(getattr(request, "user", None))
        try:
            return self.get_response(request)
        finally:
            clear_current_actor()
