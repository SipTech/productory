from __future__ import annotations

from threading import local

_state = local()


def set_current_actor(user) -> None:
    if user is not None and getattr(user, "is_authenticated", False):
        _state.actor = user
    else:
        _state.actor = None


def get_current_actor():
    return getattr(_state, "actor", None)


def clear_current_actor() -> None:
    _state.actor = None
