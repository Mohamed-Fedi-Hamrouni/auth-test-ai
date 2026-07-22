import secrets
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, cast

from flask import request, session

from auth_test_ai.errors import ApiError

F = TypeVar("F", bound=Callable[..., Any])


def issue_csrf_token() -> str:
    token = secrets.token_urlsafe(32)
    session["csrf_token"] = token
    return token


def require_csrf(view: F) -> F:
    @wraps(view)
    def wrapped(*args: object, **kwargs: object) -> Any:
        expected = session.get("csrf_token")
        supplied = request.headers.get("X-CSRFToken")
        if not isinstance(expected, str) or not isinstance(supplied, str):
            raise ApiError("CSRF_INVALID", "Invalid CSRF token.", 400)
        if not secrets.compare_digest(expected, supplied):
            raise ApiError("CSRF_INVALID", "Invalid CSRF token.", 400)
        return view(*args, **kwargs)

    return cast(F, wrapped)
