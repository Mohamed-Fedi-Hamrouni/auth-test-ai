from datetime import UTC, datetime, timedelta

from flask import current_app, session


def utc_now() -> datetime:
    return datetime.now(UTC)


def _parse(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def create_user_session(user_id: object, now: datetime | None = None) -> None:
    current = now or utc_now()
    regenerate = getattr(current_app.session_interface, "regenerate", None)
    if regenerate is not None:
        regenerate(session)
    session.clear()
    session.permanent = True
    session["user_id"] = str(user_id)
    session["issued_at"] = current.isoformat()
    session["last_activity_at"] = current.isoformat()


def get_session_user_id(now: datetime | None = None) -> str | None:
    user_id = session.get("user_id")
    issued = session.get("issued_at")
    last_activity = session.get("last_activity_at")
    if not all(isinstance(value, str) for value in (user_id, issued, last_activity)):
        session.clear()
        return None
    current = now or utc_now()
    idle_limit = timedelta(minutes=current_app.config["SESSION_IDLE_MINUTES"])
    absolute_limit = timedelta(hours=current_app.config["SESSION_ABSOLUTE_HOURS"])
    if (
        current - _parse(last_activity) > idle_limit
        or current - _parse(issued) > absolute_limit
    ):
        session.clear()
        return None
    session["last_activity_at"] = current.isoformat()
    return user_id


def destroy_session() -> None:
    session.clear()
