from dataclasses import dataclass
from datetime import datetime

from auth_test_ai.extensions import db
from auth_test_ai.models import AuthenticationFailureReason, User
from auth_test_ai.services.audit_service import record_attempt
from auth_test_ai.services.lockout_service import (
    is_locked,
    register_failure,
    register_success,
)
from auth_test_ai.services.password_service import dummy_password_hash, verify_password
from auth_test_ai.services.user_service import get_user_by_login


@dataclass(frozen=True)
class AuthenticationResult:
    user: User | None
    authenticated: bool


def authenticate(
    *,
    login: str,
    password: str,
    ip_address: str | None,
    user_agent: str | None,
    now: datetime | None = None,
) -> AuthenticationResult:
    user = get_user_by_login(login, for_update=True)
    reason = AuthenticationFailureReason.UNKNOWN_LOGIN
    authenticated = False

    hash_to_verify = dummy_password_hash()
    may_authenticate = False
    if user is not None:
        if not user.is_active:
            reason = AuthenticationFailureReason.ACCOUNT_INACTIVE
        elif is_locked(user, now):
            reason = AuthenticationFailureReason.ACCOUNT_LOCKED
        else:
            hash_to_verify = user.password_hash
            may_authenticate = True

    password_matches = verify_password(hash_to_verify, password)
    if user is not None and may_authenticate:
        if not password_matches:
            register_failure(user, now)
            reason = AuthenticationFailureReason.INVALID_PASSWORD
        else:
            register_success(user)
            reason = AuthenticationFailureReason.SUCCESS
            authenticated = True

    record_attempt(
        user=user,
        attempted_login=login,
        success=authenticated,
        reason=reason,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return AuthenticationResult(
        user=user if authenticated else None, authenticated=authenticated
    )
