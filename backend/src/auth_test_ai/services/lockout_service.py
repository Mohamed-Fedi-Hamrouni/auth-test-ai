from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from flask import current_app

from auth_test_ai.models import User

TimeProvider = Callable[[], datetime]


def utc_now() -> datetime:
    return datetime.now(UTC)


def is_locked(user: User, now: datetime | None = None) -> bool:
    current = now or utc_now()
    if user.locked_until is None:
        return False
    locked_until = user.locked_until
    if locked_until.tzinfo is None:
        locked_until = locked_until.replace(tzinfo=UTC)
    if locked_until <= current:
        user.locked_until = None
        user.failed_login_count = 0
        return False
    return True


def register_failure(user: User, now: datetime | None = None) -> None:
    current = now or utc_now()
    user.failed_login_count = (user.failed_login_count or 0) + 1
    if user.failed_login_count >= current_app.config["AUTH_MAX_FAILED_ATTEMPTS"]:
        user.locked_until = current + timedelta(
            minutes=current_app.config["AUTH_LOCKOUT_MINUTES"]
        )


def register_success(user: User) -> None:
    user.failed_login_count = 0
    user.locked_until = None
