import uuid
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, cast

from flask import g

from auth_test_ai.errors import ApiError
from auth_test_ai.extensions import db
from auth_test_ai.models import User
from auth_test_ai.services.session_service import destroy_session, get_session_user_id

F = TypeVar("F", bound=Callable[..., Any])


def login_required(view: F) -> F:
    @wraps(view)
    def wrapped(*args: object, **kwargs: object) -> Any:
        user_id = get_session_user_id()
        try:
            identifier = uuid.UUID(user_id) if user_id else None
        except ValueError:
            identifier = None
        user = db.session.get(User, identifier) if identifier else None
        if user is None or not user.is_active:
            destroy_session()
            raise ApiError("AUTH_REQUIRED", "Authentication required.", 401)
        g.current_user = user
        return view(*args, **kwargs)

    return cast(F, wrapped)


def role_required(role_name: str) -> Callable[[F], F]:
    def decorator(view: F) -> F:
        @login_required
        @wraps(view)
        def wrapped(*args: object, **kwargs: object) -> Any:
            if role_name not in {role.name for role in g.current_user.roles}:
                raise ApiError("FORBIDDEN", "Access forbidden.", 403)
            return view(*args, **kwargs)

        return cast(F, wrapped)

    return decorator
