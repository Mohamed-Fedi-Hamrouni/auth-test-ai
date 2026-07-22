import secrets
from datetime import UTC, datetime, timedelta

import pytest
from flask import Flask
from flask.testing import FlaskClient
from tests.conftest import csrf_headers

from auth_test_ai.extensions import db
from auth_test_ai.models import AuthenticationAttempt
from auth_test_ai.services.user_service import create_user

PASSWORD = "Aa" + secrets.token_urlsafe(32)


def create_account(app: Flask, login: str, roles: tuple[str, ...]):
    with app.app_context():
        user = create_user(
            first_name="Test",
            last_name="Account",
            login=login,
            password=PASSWORD,
            role_names=roles,
        )
        db.session.commit()
        return user.id


def authenticate(client: FlaskClient, login: str) -> None:
    response = client.post(
        "/api/auth/login",
        json={"login": login, "password": PASSWORD},
        headers=csrf_headers(client),
    )
    assert response.status_code == 200


@pytest.mark.integration
def test_admin_routes_require_admin_role(client: FlaskClient, app: Flask) -> None:
    assert client.get("/api/admin/users").status_code == 401
    create_account(app, "user", ("USER",))
    authenticate(client, "user")
    assert client.get("/api/admin/users").status_code == 403


@pytest.mark.integration
def test_admin_lists_and_creates_users_without_hash(
    client: FlaskClient, app: Flask
) -> None:
    create_account(app, "admin", ("USER", "ADMIN"))
    authenticate(client, "admin")
    response = client.post(
        "/api/admin/users",
        json={
            "firstName": "New",
            "lastName": "User",
            "login": "new.user",
            "password": PASSWORD,
        },
        headers=csrf_headers(client),
    )
    assert response.status_code == 201
    listing = client.get("/api/admin/users")
    assert listing.status_code == 200
    assert listing.get_json()["total"] == 2
    assert "password" not in str(listing.get_json()).lower()
    duplicate = client.post(
        "/api/admin/users",
        json={
            "firstName": "X",
            "lastName": "Y",
            "login": "NEW.USER",
            "password": PASSWORD,
        },
        headers=csrf_headers(client),
    )
    assert duplicate.status_code == 409


@pytest.mark.integration
def test_admin_disables_user_and_lists_safe_attempts(
    client: FlaskClient, app: Flask
) -> None:
    create_account(app, "admin", ("USER", "ADMIN"))
    target = create_account(app, "target", ("USER",))
    target_client = app.test_client()
    authenticate(target_client, "target")
    assert target_client.get("/api/auth/me").status_code == 200
    authenticate(client, "admin")
    response = client.patch(
        f"/api/admin/users/{target}/status",
        json={"isActive": False},
        headers=csrf_headers(client),
    )
    assert response.status_code == 200
    assert target_client.get("/api/auth/me").status_code == 401
    attempts = client.get("/api/admin/auth-attempts")
    assert attempts.status_code == 200
    body = str(attempts.get_json()).lower()
    assert "ip_address" not in body and "internal_failure_reason" not in body


@pytest.mark.integration
def test_seed_command_is_idempotent(
    app: Flask, clean_database: None, seed_passwords: None
) -> None:
    del clean_database
    del seed_passwords
    runner = app.test_cli_runner()
    assert runner.invoke(args=["seed-dev-users"]).exit_code == 0
    assert runner.invoke(args=["seed-dev-users"]).exit_code == 0
    with app.app_context():
        from auth_test_ai.models import User

        assert db.session.query(User).count() == 5


@pytest.mark.integration
def test_admin_mutations_require_valid_csrf(client: FlaskClient, app: Flask) -> None:
    create_account(app, "admin", ("USER", "ADMIN"))
    target = create_account(app, "target", ("USER",))
    authenticate(client, "admin")
    payload = {
        "firstName": "New",
        "lastName": "User",
        "login": "new.user",
        "password": PASSWORD,
    }
    assert client.post("/api/admin/users", json=payload).status_code == 400
    assert (
        client.post(
            "/api/admin/users", json=payload, headers={"X-CSRFToken": "invalid"}
        ).status_code
        == 400
    )
    assert (
        client.patch(
            f"/api/admin/users/{target}/status", json={"isActive": False}
        ).status_code
        == 400
    )
    assert (
        client.patch(
            f"/api/admin/users/{target}/status",
            json={"isActive": False},
            headers={"X-CSRFToken": "invalid"},
        ).status_code
        == 400
    )


@pytest.mark.integration
def test_logout_requires_valid_csrf(client: FlaskClient, app: Flask) -> None:
    create_account(app, "user", ("USER",))
    authenticate(client, "user")
    assert client.post("/api/auth/logout").status_code == 400
    assert (
        client.post("/api/auth/logout", headers={"X-CSRFToken": "invalid"}).status_code
        == 400
    )


@pytest.mark.integration
def test_audit_pagination_boundaries_and_safe_filters(
    client: FlaskClient, app: Flask
) -> None:
    admin_id = create_account(app, "admin", ("USER", "ADMIN"))
    authenticate(client, "admin")
    assert client.get("/api/admin/auth-attempts?limit=101").status_code == 400
    assert client.get("/api/admin/auth-attempts?page=0").status_code == 400
    other_id = create_account(app, "other", ("USER",))
    now = datetime(2020, 7, 21, 12, tzinfo=UTC)
    with app.app_context():
        matching = AuthenticationAttempt(
            user_id=admin_id,
            attempted_login="admin",
            success=True,
            internal_failure_reason="SUCCESS",
            ip_address_hash="a" * 64,
            user_agent="private-agent",
            created_at=now,
        )
        nonmatching_success = AuthenticationAttempt(
            user_id=other_id,
            attempted_login="other",
            success=True,
            internal_failure_reason="SUCCESS",
            ip_address_hash="b" * 64,
            user_agent="private-agent",
            created_at=now - timedelta(days=2),
        )
        nonmatching_failure = AuthenticationAttempt(
            user_id=admin_id,
            attempted_login="admin",
            success=False,
            internal_failure_reason="INVALID_PASSWORD",
            ip_address_hash="c" * 64,
            user_agent="private-agent",
            created_at=now,
        )
        db.session.add_all([matching, nonmatching_success, nonmatching_failure])
        db.session.commit()
        matching_id = str(matching.id)
        failure_id = str(nonmatching_failure.id)
    start = (now - timedelta(hours=1)).isoformat()
    end = (now + timedelta(hours=1)).isoformat()
    response = client.get(
        "/api/admin/auth-attempts",
        query_string={
            "success": "true",
            "user_id": str(admin_id),
            "date_from": start,
            "date_to": end,
            "page": 1,
            "limit": 1,
        },
    )
    body = response.get_json()
    assert response.status_code == 200
    assert body["total"] == 1
    assert [item["id"] for item in body["items"]] == [matching_id]
    failure = client.get(
        "/api/admin/auth-attempts", query_string={"success": "false"}
    ).get_json()
    assert failure_id in {item["id"] for item in failure["items"]}
    serialized = str(body).lower()
    for forbidden in (
        "ip_address_hash",
        "private-agent",
        "internal_failure_reason",
        "session",
    ):
        assert forbidden not in serialized


@pytest.mark.integration
def test_seed_safety_and_missing_values(
    app: Flask, clean_database: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    del clean_database
    runner = app.test_cli_runner()
    monkeypatch.delenv("ALLOW_DEV_SEED", raising=False)
    assert runner.invoke(args=["seed-dev-users"]).exit_code != 0
    monkeypatch.setenv("ALLOW_DEV_SEED", "true")
    monkeypatch.setenv("SEED_USER_ONE_PASSWORD", "must-not-appear-in-output")
    result = runner.invoke(args=["seed-dev-users"])
    assert result.exit_code != 0
    assert "SEED_ADMIN_PASSWORD" in result.output
    assert "must-not-appear-in-output" not in result.output
    with monkeypatch.context() as scoped:
        scoped.setitem(app.config, "ENVIRONMENT", "production")
        assert runner.invoke(args=["seed-dev-users"]).exit_code != 0
