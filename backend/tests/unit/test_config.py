import secrets

import pytest

from auth_test_ai import create_app
from auth_test_ai.config import (
    DEMONSTRATION_SECRET,
    MAXIMUM_SECRET_LENGTH,
    DevelopmentConfig,
    ProductionConfig,
    TestingConfig,
    is_acceptable_production_secret,
)


@pytest.mark.unit
def test_cookie_security_by_environment() -> None:
    assert DevelopmentConfig.SESSION_COOKIE_SECURE is False
    assert TestingConfig.SESSION_COOKIE_SECURE is False
    assert ProductionConfig.SESSION_COOKIE_SECURE is True
    assert ProductionConfig.SESSION_COOKIE_HTTPONLY is True
    assert ProductionConfig.SESSION_COOKIE_SAMESITE == "Lax"


@pytest.mark.unit
def test_production_rejects_missing_or_unsafe_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(ProductionConfig, "SECRET_KEY", None)
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        ProductionConfig.validate()


@pytest.mark.unit
def test_production_requires_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        ProductionConfig, "SECRET_KEY", "qB7_mN2-Zx9Lp4_Vc8Ks1-Wd6Yr3_Ht5"
    )
    monkeypatch.setattr(ProductionConfig, "DATABASE_URL", None)
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        ProductionConfig.validate()


@pytest.mark.unit
@pytest.mark.parametrize(
    "database_url",
    [
        "sqlite:///production.db",
        "mysql://user:password@localhost/database",
        "malformed database text",
        "postgresql+psycopg://user:password@localhost",
        "postgresql+asyncpg://user:password@localhost/database",
        "postgresql://user:password@localhost/database",
    ],
)
def test_production_rejects_invalid_or_unsupported_database_urls(
    database_url: str,
) -> None:
    values = {
        "SECRET_KEY": "qB7_mN2-Zx9Lp4_Vc8Ks1-Wd6Yr3_Ht5",
        "DATABASE_URL": database_url,
        "RATELIMIT_STORAGE_URI": "redis://rate-limit.invalid/0",
    }
    with pytest.raises(RuntimeError, match="PostgreSQL DATABASE_URL"):
        ProductionConfig.validate(values)


@pytest.mark.unit
def test_production_accepts_supported_postgresql_url() -> None:
    ProductionConfig.validate(
        {
            "SECRET_KEY": "qB7_mN2-Zx9Lp4_Vc8Ks1-Wd6Yr3_Ht5",
            "DATABASE_URL": "postgresql+psycopg://user:password@db.invalid/app",
            "RATELIMIT_STORAGE_URI": "redis://rate-limit.invalid/0",
        }
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    "database_url",
    [
        "postgresql+psycopg://host:not-a-port/app",
        "postgresql+psycopg://host:0/app",
        "postgresql+psycopg://host:65536/app",
        "postgresql+psycopg://host:70000/app",
    ],
)
def test_production_rejects_invalid_postgresql_ports(database_url: str) -> None:
    values = {
        "SECRET_KEY": "qB7_mN2-Zx9Lp4_Vc8Ks1-Wd6Yr3_Ht5",
        "DATABASE_URL": database_url,
        "RATELIMIT_STORAGE_URI": "redis://rate-limit.invalid/0",
    }
    with pytest.raises(RuntimeError, match="PostgreSQL DATABASE_URL"):
        ProductionConfig.validate(values)


@pytest.mark.unit
@pytest.mark.parametrize(
    "database_url",
    [
        "postgresql+psycopg://host/app",
        "postgresql+psycopg://host:1/app",
        "postgresql+psycopg://host:5432/app",
        "postgresql+psycopg://host:65535/app",
        "postgresql+psycopg:///app",
    ],
)
def test_production_accepts_valid_postgresql_ports(database_url: str) -> None:
    ProductionConfig.validate(
        {
            "SECRET_KEY": "qB7_mN2-Zx9Lp4_Vc8Ks1-Wd6Yr3_Ht5",
            "DATABASE_URL": database_url,
            "RATELIMIT_STORAGE_URI": "redis://rate-limit.invalid/0",
        }
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    "secret",
    [
        None,
        DEMONSTRATION_SECRET,
        "development-only-replace-with-a-random-secret",
        "a" * 64,
        "predictable-example-secret-value-123456",
        "12345678901234567890123456789012",
        "abcdefghijklmnopqrstuvwxyzabcdef",
        "0123456789abcdef0123456789abcdef",
        "Ab1_Ab1_Ab1_Ab1_Ab1_Ab1_Ab1_Ab1_",
        ("Ab1_" * 8) + "Xy7-",
        ("Z9-" * 10) + "suffix",
        "prefix" + ("Q2_" * 10),
        "too-short",
    ],
)
def test_production_secret_validation_rejects_weak_values(secret: object) -> None:
    assert not is_acceptable_production_secret(secret)


@pytest.mark.unit
def test_explicit_environments_and_fail_closed_selection(
    monkeypatch: pytest.MonkeyPatch, mocker
) -> None:
    mocker.patch("auth_test_ai.init_extensions")
    assert create_app("development").config["ENVIRONMENT"] == "development"
    assert create_app("testing").config["TESTING"] is True
    monkeypatch.delenv("AUTH_TEST_AI_ENV", raising=False)
    with pytest.raises(RuntimeError, match="AUTH_TEST_AI_ENV"):
        create_app()
    monkeypatch.setenv("AUTH_TEST_AI_ENV", "invalid")
    with pytest.raises(RuntimeError, match="Unknown"):
        create_app()


@pytest.mark.unit
def test_factory_rejects_class_and_dictionary_configuration() -> None:
    with pytest.raises(TypeError, match="environment name"):
        create_app(ProductionConfig)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="environment name"):
        create_app({"TESTING": True})  # type: ignore[arg-type]


@pytest.mark.unit
@pytest.mark.parametrize(
    "storage_uri",
    [
        "memory://",
        "memory://local",
        "async+memory://",
        "async+memory://local",
        "malformed URI",
        "file:///tmp/rate-limit",
        " redis://host/0",
        "redis://host/0 ",
        " redis://host/0 ",
        "redis://ho\tst/0",
        "redis://%20/0",
        "redis://%09/0",
        "redis:///0",
        "redis://host:not-a-port/0",
        "redis://host:0/0",
        "redis://host:65536/0",
        "redis://host:70000/0",
    ],
)
def test_production_requires_supported_shared_rate_limit_storage(
    storage_uri: str,
) -> None:
    values = {
        "SECRET_KEY": "qB7_mN2-Zx9Lp4_Vc8Ks1-Wd6Yr3_Ht5",
        "DATABASE_URL": "postgresql+psycopg://example.invalid/app",
        "RATELIMIT_STORAGE_URI": storage_uri,
    }
    with pytest.raises(RuntimeError, match="RATELIMIT_STORAGE_URI"):
        ProductionConfig.validate(values)


@pytest.mark.unit
@pytest.mark.parametrize(
    "storage_uri",
    [
        "redis://shared.invalid/0",
        "redis://shared.invalid:1/0",
        "redis://shared.invalid:6379/0",
        "redis://shared.invalid:65535/0",
        "rediss://user:secret@shared.invalid:6380/0",
    ],
)
def test_production_accepts_shared_rate_limit_storage_without_connecting(
    storage_uri: str,
) -> None:
    ProductionConfig.validate(
        {
            "SECRET_KEY": "qB7_mN2-Zx9Lp4_Vc8Ks1-Wd6Yr3_Ht5",
            "DATABASE_URL": "postgresql+psycopg://example.invalid/app",
            "RATELIMIT_STORAGE_URI": storage_uri,
        }
    )


@pytest.mark.unit
def test_explicit_production_runs_validation(
    monkeypatch: pytest.MonkeyPatch, mocker
) -> None:
    mocker.patch("auth_test_ai.init_extensions")
    monkeypatch.setenv("SECRET_KEY", "qB7_mN2-Zx9Lp4_Vc8Ks1-Wd6Yr3_Ht5")
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql+psycopg://service.invalid/application"
    )
    monkeypatch.setenv("RATELIMIT_STORAGE_URI", "redis://service.invalid/0")
    app = create_app("production")
    assert app.config["ENVIRONMENT"] == "production"
    assert app.config["SESSION_COOKIE_SECURE"] is True


@pytest.mark.unit
@pytest.mark.parametrize(
    "secret",
    [
        "qB7_mN2-Zx9Lp4_Vc8Ks1-Wd6Yr3_Ht5",
        "R8v_W2m-J7qX4_cN9pL6-Ys3_Kd5Tz1B",
    ],
)
def test_production_secret_validation_accepts_token_urlsafe_style(
    secret: str,
) -> None:
    assert is_acceptable_production_secret(secret)


@pytest.mark.unit
def test_production_secret_validation_accepts_exact_maximum_length() -> None:
    secret = secrets.token_urlsafe(192)
    assert len(secret) == MAXIMUM_SECRET_LENGTH
    assert is_acceptable_production_secret(secret)


@pytest.mark.unit
def test_production_secret_validation_rejects_above_maximum_before_pattern_scan(
    mocker,
) -> None:
    repeated_pattern_scan = mocker.patch(
        "auth_test_ai.config._has_predominant_repeating_pattern"
    )
    secret = secrets.token_urlsafe(192) + "X"
    assert len(secret) == MAXIMUM_SECRET_LENGTH + 1
    assert not is_acceptable_production_secret(secret)
    repeated_pattern_scan.assert_not_called()


@pytest.mark.unit
def test_invalid_test_database_is_rejected_before_extensions(
    monkeypatch: pytest.MonkeyPatch, mocker
) -> None:
    initialize = mocker.patch("auth_test_ai.init_extensions")
    monkeypatch.setattr(
        TestingConfig,
        "SQLALCHEMY_DATABASE_URI",
        "postgresql+psycopg://localhost/auth_test_ai",
    )
    with pytest.raises(RuntimeError, match="auth_test_ai_test"):
        create_app("testing")
    initialize.assert_not_called()
