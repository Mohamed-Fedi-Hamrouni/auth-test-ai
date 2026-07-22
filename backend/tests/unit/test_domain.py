from datetime import UTC, datetime, timedelta

import pytest
from flask import Flask
from sqlalchemy.dialects import postgresql

from auth_test_ai.models import Role, User
from auth_test_ai.services.audit_service import anonymize_ip
from auth_test_ai.services.lockout_service import is_locked, register_failure
from auth_test_ai.services.user_service import normalize_login


@pytest.fixture()
def domain_app() -> Flask:
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY="unit-test-secret-key",
        AUTH_MAX_FAILED_ATTEMPTS=5,
        AUTH_LOCKOUT_MINUTES=15,
    )
    return app


@pytest.mark.unit
def test_locked_lookup_uses_select_for_update() -> None:
    from auth_test_ai.services.user_service import user_lookup_statement

    compiled = str(
        user_lookup_statement("example", for_update=True).compile(
            dialect=postgresql.dialect()
        )
    )
    assert "FOR UPDATE" in compiled


@pytest.mark.unit
def test_normalize_login_trims_casefolds_and_normalizes_unicode() -> None:
    assert normalize_login("  Straße  ") == "strasse"


@pytest.mark.unit
def test_lockout_calculation_and_expiration(domain_app: Flask) -> None:
    now = datetime(2026, 7, 21, tzinfo=UTC)
    user = User(
        first_name="Test",
        last_name="User",
        login="test",
        login_normalized="test",
        password_hash="redacted-hash",
    )
    with domain_app.app_context():
        for _ in range(5):
            register_failure(user, now)
        assert user.locked_until == now + timedelta(minutes=15)
        assert is_locked(user, now + timedelta(minutes=14))
        assert not is_locked(user, now + timedelta(minutes=16))
        assert user.failed_login_count == 0


@pytest.mark.unit
def test_ip_anonymization_is_stable_and_not_raw(domain_app: Flask) -> None:
    with domain_app.app_context():
        first = anonymize_ip("192.0.2.10")
        assert first == anonymize_ip("192.0.2.10")
        assert first != "192.0.2.10"
        assert len(first or "") == 64


@pytest.mark.unit
def test_public_serialization_excludes_password_hash_and_roles() -> None:
    user = User(
        first_name="Test",
        last_name="User",
        login="test",
        login_normalized="test",
        password_hash="must-not-leak",
        roles=[Role(name="USER", description="User")],
    )
    public = user.to_public_dict()
    assert "password_hash" not in public
    assert "passwordHash" not in public
    assert public["roles"] == ["USER"]
