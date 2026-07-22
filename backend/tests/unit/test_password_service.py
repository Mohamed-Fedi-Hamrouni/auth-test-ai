import pytest
from flask import Flask

from auth_test_ai.services.password_service import (
    hash_password,
    needs_rehash,
    validate_password_policy,
    verify_password,
)


@pytest.fixture()
def password_app() -> Flask:
    app = Flask(__name__)
    app.config.update(
        ARGON2_TIME_COST=1,
        ARGON2_MEMORY_COST=8192,
        ARGON2_PARALLELISM=1,
    )
    return app


@pytest.mark.unit
@pytest.mark.parametrize("length", [0, 14])
def test_password_minimum_length(length: int) -> None:
    errors = validate_password_policy("a" * length)
    assert [error.code for error in errors] == ["PASSWORD_TOO_SHORT"]


@pytest.mark.unit
def test_password_maximum_length() -> None:
    assert validate_password_policy("a" * 128) == []
    assert validate_password_policy("a" * 129)[0].code == "PASSWORD_TOO_LONG"


@pytest.mark.unit
def test_password_accepts_unicode_and_spaces() -> None:
    assert validate_password_policy("mot de passe très long 🔒") == []


@pytest.mark.unit
def test_argon2id_hash_and_verification(password_app: Flask) -> None:
    with password_app.app_context():
        first = hash_password("Correct horse battery staple")
        second = hash_password("Correct horse battery staple")
        assert first != second
        assert first.startswith("$argon2id$")
        assert verify_password(first, "Correct horse battery staple")
        assert not verify_password(first, "correct horse battery staple")
        assert not needs_rehash(first)


@pytest.mark.unit
def test_needs_rehash_for_invalid_hash(password_app: Flask) -> None:
    with password_app.app_context():
        assert needs_rehash("not-a-hash")


@pytest.mark.unit
def test_needs_rehash_when_argon2_parameters_change(password_app: Flask) -> None:
    with password_app.app_context():
        password_hash = hash_password("Correct horse battery staple")
        password_app.config["ARGON2_TIME_COST"] = 2
        assert needs_rehash(password_hash)
