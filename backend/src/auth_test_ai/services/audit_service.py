import hashlib
import hmac

from flask import current_app

from auth_test_ai.extensions import db
from auth_test_ai.models import AuthenticationAttempt, AuthenticationFailureReason, User
from auth_test_ai.services.user_service import normalize_login


def anonymize_ip(ip_address: str | None) -> str | None:
    if not ip_address:
        return None
    key = current_app.config["SECRET_KEY"].encode()
    return hmac.new(key, ip_address.encode(), hashlib.sha256).hexdigest()


def record_attempt(
    *,
    user: User | None,
    attempted_login: str,
    success: bool,
    reason: AuthenticationFailureReason,
    ip_address: str | None,
    user_agent: str | None,
) -> AuthenticationAttempt:
    attempt = AuthenticationAttempt(
        user=user,
        attempted_login=normalize_login(attempted_login[:100])[:100],
        success=success,
        internal_failure_reason=reason.value,
        ip_address_hash=anonymize_ip(ip_address),
        user_agent=user_agent[:255] if user_agent else None,
    )
    db.session.add(attempt)
    return attempt
