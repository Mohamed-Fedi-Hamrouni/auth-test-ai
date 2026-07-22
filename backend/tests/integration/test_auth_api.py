import secrets
from datetime import UTC, datetime, timedelta

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import LargeBinary, String, select
from tests.conftest import csrf_headers

from auth_test_ai.extensions import db
from auth_test_ai.models import AuthenticationAttempt, User
from auth_test_ai.services.password_service import dummy_password_hash
from auth_test_ai.services.user_service import create_user, normalize_login

PASSWORD = "Aa" + secrets.token_urlsafe(32)
WRONG_PASSWORD = "Bb" + secrets.token_urlsafe(32)


def add_user(app: Flask, *, login: str = "Example.User", active: bool = True):
    with app.app_context():
        user = create_user(
            first_name="Ahmed",
            last_name="Ben Ali",
            login=login,
            password=PASSWORD,
            is_active=active,
        )
        db.session.commit()
        return user.id


def login(client: FlaskClient, login_value: str, password: str = PASSWORD):
    return client.post(
        "/api/auth/login",
        json={"login": login_value, "password": password},
        headers=csrf_headers(client),
    )


@pytest.mark.integration
def test_health_and_csrf_contract(client: FlaskClient) -> None:
    assert client.get("/api/health").get_json() == {"status": "ok"}
    response = client.get("/api/auth/csrf")
    assert response.status_code == 200
    assert isinstance(response.get_json()["csrfToken"], str)


@pytest.mark.integration
def test_login_requires_valid_csrf(client: FlaskClient, app: Flask) -> None:
    add_user(app)
    missing = client.post(
        "/api/auth/login", json={"login": "Example.User", "password": PASSWORD}
    )
    invalid = client.post(
        "/api/auth/login",
        json={"login": "Example.User", "password": PASSWORD},
        headers={"X-CSRFToken": "invalid"},
    )
    assert missing.status_code == invalid.status_code == 400
    assert missing.get_json()["error"]["code"] == "CSRF_INVALID"
    headers = csrf_headers(client)
    cookie_name = app.config["SESSION_COOKIE_NAME"]
    anonymous_cookie = client.get_cookie(cookie_name)
    assert anonymous_cookie is not None
    assert (
        client.post(
            "/api/auth/login",
            json={"login": "Example.User", "password": PASSWORD},
            headers=headers,
        ).status_code
        == 200
    )
    authenticated_cookie = client.get_cookie(cookie_name)
    assert authenticated_cookie is not None
    assert authenticated_cookie.value != anonymous_cookie.value


@pytest.mark.integration
def test_successful_login_normalization_me_and_logout(
    client: FlaskClient, app: Flask
) -> None:
    add_user(app)
    response = login(client, "  example.USER  ")
    assert response.status_code == 200
    assert response.get_json()["message"] == "Welcome Ahmed Ben Ali"
    assert "password_hash" not in str(response.get_json())
    assert client.get("/api/auth/me").status_code == 200
    logout = client.post("/api/auth/logout", headers=csrf_headers(client))
    assert (logout.status_code, logout.get_json(silent=True)) == (204, None)
    assert client.get("/api/auth/me").status_code == 401
    with app.app_context():
        session_model = app.session_interface.sql_session_model
        assert db.session.query(session_model).count() == 0


@pytest.mark.integration
@pytest.mark.parametrize(
    ("login_value", "password"),
    [("unknown", PASSWORD), ("Example.User", WRONG_PASSWORD)],
)
def test_invalid_credentials_are_generic(
    client: FlaskClient, app: Flask, login_value: str, password: str
) -> None:
    add_user(app)
    response = login(client, login_value, password)
    assert response.status_code == 401
    assert response.get_json()["error"]["message"] == "Invalid login or password."


@pytest.mark.integration
def test_password_is_case_sensitive_and_required_fields(
    client: FlaskClient, app: Flask
) -> None:
    add_user(app)
    assert login(client, "Example.User", PASSWORD.swapcase()).status_code == 401
    for payload in (
        {"login": "", "password": PASSWORD},
        {"login": "x", "password": ""},
    ):
        response = client.post(
            "/api/auth/login", json=payload, headers=csrf_headers(client)
        )
        assert response.status_code == 400
        assert response.get_json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.integration
def test_inactive_account_and_audit(client: FlaskClient, app: Flask) -> None:
    add_user(app, active=False)
    response = login(client, "Example.User")
    assert response.status_code == 401
    with app.app_context():
        attempt = db.session.scalar(select(AuthenticationAttempt))
        assert attempt is not None and not attempt.success
        assert attempt.internal_failure_reason == "ACCOUNT_INACTIVE"
        assert attempt.ip_address_hash is not None


@pytest.mark.integration
def test_lockout_after_five_failures_and_success_after_expiration(
    client: FlaskClient, app: Flask
) -> None:
    user_id = add_user(app)
    for _ in range(5):
        assert login(client, "Example.User", WRONG_PASSWORD).status_code == 401
    assert login(client, "Example.User").status_code == 401
    with app.app_context():
        persisted = db.session.get(User, user_id)
        assert persisted is not None
        persisted.locked_until = datetime.now(UTC) - timedelta(minutes=1)
        db.session.commit()
    assert login(client, "Example.User").status_code == 200
    with app.app_context():
        persisted = db.session.get(User, user_id)
        assert persisted is not None and persisted.failed_login_count == 0


@pytest.mark.integration
def test_session_idle_and_absolute_expiration(client: FlaskClient, app: Flask) -> None:
    add_user(app)
    assert login(client, "Example.User").status_code == 200
    with client.session_transaction() as user_session:
        user_session["last_activity_at"] = (
            datetime.now(UTC) - timedelta(minutes=31)
        ).isoformat()
    assert client.get("/api/auth/me").status_code == 401
    assert login(client, "Example.User").status_code == 200
    with client.session_transaction() as user_session:
        user_session["issued_at"] = (datetime.now(UTC) - timedelta(hours=9)).isoformat()
    assert client.get("/api/auth/me").status_code == 401


@pytest.mark.integration
def test_success_and_failure_audits(client: FlaskClient, app: Flask) -> None:
    add_user(app)
    assert login(client, "Example.User", WRONG_PASSWORD).status_code == 401
    assert login(client, "Example.User").status_code == 200
    with app.app_context():
        attempts = db.session.scalars(
            select(AuthenticationAttempt).order_by(AuthenticationAttempt.created_at)
        ).all()
        assert [attempt.success for attempt in attempts] == [False, True]


@pytest.mark.integration
def test_argon_verification_selects_exact_real_or_cached_dummy_hash(
    client: FlaskClient, app: Flask, mocker
) -> None:
    active_id = add_user(app, login="active")
    add_user(app, login="inactive", active=False)
    locked_id = add_user(app, login="locked")
    with app.app_context():
        active_hash = db.session.get(User, active_id).password_hash
        locked = db.session.get(User, locked_id)
        locked.locked_until = datetime.now(UTC) + timedelta(minutes=10)
        db.session.commit()
        dummy_hash = dummy_password_hash()
        assert dummy_password_hash() is dummy_hash
    verify = mocker.patch(
        "auth_test_ai.services.authentication_service.verify_password",
        wraps=__import__(
            "auth_test_ai.services.password_service", fromlist=["verify_password"]
        ).verify_password,
    )
    cases = (
        ("active", PASSWORD, 200, active_hash),
        ("active", WRONG_PASSWORD, 401, active_hash),
        ("unknown", PASSWORD, 401, dummy_hash),
        ("inactive", PASSWORD, 401, dummy_hash),
        ("locked", PASSWORD, 401, dummy_hash),
    )
    for login_value, password, status, expected_hash in cases:
        verify.reset_mock()
        assert login(client, login_value, password).status_code == status
        verify.assert_called_once_with(expected_hash, password)
    with app.app_context():
        attempts = db.session.scalars(select(AuthenticationAttempt)).all()
        assert all(WRONG_PASSWORD not in repr(attempt) for attempt in attempts)
        assert all(
            WRONG_PASSWORD not in attempt.attempted_login for attempt in attempts
        )


@pytest.mark.integration
def test_credential_and_request_size_limits(client: FlaskClient, app: Flask) -> None:
    add_user(app, login="x" * 100)
    assert login(client, "x" * 100).status_code == 200
    assert login(client, "x" * 101).status_code == 400
    assert login(client, "x", "p" * 128).status_code == 401
    assert login(client, "x", "p" * 129).status_code == 400
    oversized = client.post(
        "/api/auth/login",
        data=b"{" + b"x" * (app.config["MAX_CONTENT_LENGTH"] + 1),
        content_type="application/json",
        headers=csrf_headers(client),
    )
    assert oversized.status_code == 413
    assert oversized.get_json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.integration
def test_sessions_are_isolated_and_modified_cookie_is_refused(
    client: FlaskClient, app: Flask
) -> None:
    add_user(app, login="first")
    add_user(app, login="second")
    second_client = app.test_client()
    assert login(client, "first").status_code == 200
    assert login(second_client, "second").status_code == 200
    assert client.get("/api/auth/me").get_json()["user"]["login"] == "first"
    assert second_client.get("/api/auth/me").get_json()["user"]["login"] == "second"
    cookie_name = app.config["SESSION_COOKIE_NAME"]
    client.set_cookie(cookie_name, "modified-opaque-session-id")
    assert client.get("/api/auth/me").status_code == 401


@pytest.mark.integration
def test_success_resets_non_locking_failure_and_logout_cookie_attributes(
    client: FlaskClient, app: Flask
) -> None:
    user_id = add_user(app)
    assert login(client, "Example.User", WRONG_PASSWORD).status_code == 401
    assert login(client, "Example.User").status_code == 200
    with app.app_context():
        assert db.session.get(User, user_id).failed_login_count == 0
    response = client.post("/api/auth/logout", headers=csrf_headers(client))
    cookie = "\n".join(response.headers.getlist("Set-Cookie"))
    assert "Expires=Thu, 01 Jan 1970" in cookie
    assert "HttpOnly" in cookie and "SameSite=Lax" in cookie


@pytest.mark.integration
def test_login_rate_limit_bounds_audit_and_returns_generic_json(
    client: FlaskClient, app: Flask
) -> None:
    from auth_test_ai.extensions import limiter

    original_limit = app.config["LOGIN_RATE_LIMIT"]
    original_enabled = limiter.enabled
    limiter.reset()
    app.config["LOGIN_RATE_LIMIT"] = "2 per minute"
    limiter.enabled = True
    try:
        oversized_login = "Oversized.Login-" + ("x" * 120)
        submitted_password = "NeverPersist-" + secrets.token_urlsafe(32)
        responses = [
            login(client, oversized_login, submitted_password) for _ in range(3)
        ]
        assert responses[-1].status_code == 429
        assert responses[-1].get_json()["error"] == {
            "code": "RATE_LIMITED",
            "message": "Too many requests.",
            "details": {},
        }
        with app.app_context():
            attempts = db.session.scalars(select(AuthenticationAttempt)).all()
            rate_limited = next(
                attempt
                for attempt in attempts
                if attempt.internal_failure_reason == "RATE_LIMITED"
            )
            expected_login = normalize_login(oversized_login[:100])[:100]
            assert rate_limited.attempted_login == expected_login
            assert len(rate_limited.attempted_login) <= 100
            assert oversized_login not in rate_limited.attempted_login
            assert rate_limited.internal_failure_reason == "RATE_LIMITED"
            assert rate_limited.ip_address_hash is not None
            assert rate_limited.ip_address_hash != "127.0.0.1"
            assert len(rate_limited.ip_address_hash) == 64
            for attempt in attempts:
                for column in AuthenticationAttempt.__table__.columns:
                    if not isinstance(column.type, (String, LargeBinary)):
                        continue
                    persisted_value = getattr(attempt, column.name)
                    if isinstance(persisted_value, bytes):
                        assert submitted_password.encode() not in persisted_value
                        assert oversized_login.encode() not in persisted_value
                    elif persisted_value is not None:
                        assert submitted_password not in persisted_value
                        assert oversized_login not in persisted_value
    finally:
        limiter.reset()
        limiter.enabled = original_enabled
        app.config["LOGIN_RATE_LIMIT"] = original_limit


@pytest.mark.integration
def test_login_invalidates_anonymous_csrf_token(
    client: FlaskClient, app: Flask
) -> None:
    add_user(app)
    anonymous_response = client.get("/api/auth/csrf")
    anonymous_token = anonymous_response.get_json()["csrfToken"]
    cookie_name = app.config["SESSION_COOKIE_NAME"]
    anonymous_sid = client.get_cookie(cookie_name).value
    assert (
        client.post(
            "/api/auth/login",
            json={"login": "Example.User", "password": PASSWORD},
            headers={"X-CSRFToken": anonymous_token},
        ).status_code
        == 200
    )
    assert client.get_cookie(cookie_name).value != anonymous_sid
    rejected = client.post("/api/auth/logout", headers={"X-CSRFToken": anonymous_token})
    assert rejected.status_code == 400
    assert rejected.get_json()["error"]["code"] == "CSRF_INVALID"
    assert (
        client.post("/api/auth/logout", headers=csrf_headers(client)).status_code == 204
    )


@pytest.mark.integration
def test_production_style_logout_cookie_is_secure(
    client: FlaskClient, app: Flask, monkeypatch: pytest.MonkeyPatch
) -> None:
    add_user(app)
    assert login(client, "Example.User").status_code == 200
    with monkeypatch.context() as scoped:
        scoped.setitem(app.config, "SESSION_COOKIE_SECURE", True)
        response = client.post("/api/auth/logout", headers=csrf_headers(client))
    deletion_headers = [
        header
        for header in response.headers.getlist("Set-Cookie")
        if "Expires=Thu, 01 Jan 1970" in header or "Max-Age=0" in header
    ]
    assert any(
        all(
            attribute in header
            for attribute in ("HttpOnly", "Secure", "SameSite=Lax", "Path=/")
        )
        for header in deletion_headers
    )
