import secrets
from collections.abc import Iterator

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import text
from sqlalchemy.engine import make_url

from auth_test_ai import create_app
from auth_test_ai.extensions import db, limiter


@pytest.fixture(scope="session")
def app() -> Flask:
    application = create_app("testing")
    database_name = make_url(application.config["SQLALCHEMY_DATABASE_URI"]).database
    if database_name != "auth_test_ai_test":
        raise RuntimeError("Integration tests require the auth_test_ai_test database")
    return application


@pytest.fixture()
def clean_database(app: Flask) -> Iterator[None]:
    with app.app_context():
        limiter.reset()
        db.session.execute(
            text(
                "TRUNCATE TABLE authentication_attempts, user_roles, users, roles, "
                "server_sessions RESTART IDENTITY CASCADE"
            )
        )
        db.session.commit()
        yield
        db.session.rollback()


@pytest.fixture()
def client(app: Flask, clean_database: None) -> FlaskClient:
    del clean_database
    return app.test_client()


@pytest.fixture()
def seed_passwords(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALLOW_DEV_SEED", "true")
    for name in (
        "ADMIN",
        "USER_ONE",
        "USER_TWO",
        "INACTIVE",
        "LOCKOUT",
    ):
        monkeypatch.setenv(f"SEED_{name}_PASSWORD", secrets.token_urlsafe(32))


def csrf_headers(client: FlaskClient) -> dict[str, str]:
    response = client.get("/api/auth/csrf")
    return {"X-CSRFToken": response.get_json()["csrfToken"]}
