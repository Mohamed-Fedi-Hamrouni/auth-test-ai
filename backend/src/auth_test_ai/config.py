import os
import re
from datetime import timedelta
from urllib.parse import quote_plus, unquote, urlparse, urlsplit

from dotenv import load_dotenv
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

load_dotenv()

ENVIRONMENT_VARIABLE = "AUTH_TEST_AI_ENV"
DEMONSTRATION_SECRET = "REPLACE_WITH_RANDOM_PRODUCTION_SECRET"
MINIMUM_SECRET_LENGTH = 32
MAXIMUM_SECRET_LENGTH = 256
PRODUCTION_DATABASE_DRIVER = "postgresql+psycopg"
PRODUCTION_RATE_LIMIT_STORAGE_SCHEMES = frozenset({"redis", "rediss"})


def _int_env(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)))


def _database_url(database_name: str) -> str:
    user = quote_plus(os.getenv("POSTGRES_USER", "auth_test_ai"))
    password = quote_plus(
        os.getenv("POSTGRES_PASSWORD", "change-me-for-local-development")
    )
    port = os.getenv("POSTGRES_PORT", "5432")
    return f"postgresql+psycopg://{user}:{password}@localhost:{port}/{database_name}"


class BaseConfig:
    """Shared secure application configuration."""

    DATABASE_URL = os.getenv("DATABASE_URL", _database_url("auth_test_ai"))
    TEST_DATABASE_URL = os.getenv(
        "TEST_DATABASE_URL", _database_url("auth_test_ai_test")
    )
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "development-only-change-me")
    SESSION_TYPE = "sqlalchemy"
    SESSION_SQLALCHEMY_TABLE = "server_sessions"
    SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "auth_test_ai_session")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=_int_env("SESSION_IDLE_MINUTES", 30))
    SESSION_IDLE_MINUTES = _int_env("SESSION_IDLE_MINUTES", 30)
    SESSION_ABSOLUTE_HOURS = _int_env("SESSION_ABSOLUTE_HOURS", 8)
    AUTH_MAX_FAILED_ATTEMPTS = _int_env("AUTH_MAX_FAILED_ATTEMPTS", 5)
    AUTH_LOCKOUT_MINUTES = _int_env("AUTH_LOCKOUT_MINUTES", 15)
    LOGIN_RATE_LIMIT = os.getenv("LOGIN_RATE_LIMIT", "10 per minute")
    MAX_CONTENT_LENGTH = _int_env("MAX_CONTENT_LENGTH", 16 * 1024)
    ARGON2_TIME_COST = _int_env("ARGON2_TIME_COST", 3)
    ARGON2_MEMORY_COST = _int_env("ARGON2_MEMORY_COST", 65536)
    ARGON2_PARALLELISM = _int_env("ARGON2_PARALLELISM", 4)
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
    JSON_SORT_KEYS = True


class DevelopmentConfig(BaseConfig):
    """Local HTTP development configuration."""

    DEBUG = True
    SESSION_COOKIE_SECURE = False


class TestingConfig(BaseConfig):
    """Dedicated PostgreSQL test configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = BaseConfig.TEST_DATABASE_URL
    SECRET_KEY = "testing-only-secret-key-not-for-production"
    SESSION_COOKIE_SECURE = False
    ARGON2_TIME_COST = 1
    ARGON2_MEMORY_COST = 8192
    ARGON2_PARALLELISM = 1
    RATELIMIT_ENABLED = True

    @classmethod
    def validate(cls, values: dict[str, object]) -> None:
        database_url = str(values.get("SQLALCHEMY_DATABASE_URI") or "")
        parsed = urlparse(database_url)
        if parsed.scheme not in {"postgresql", "postgresql+psycopg"}:
            raise RuntimeError("Testing requires a PostgreSQL TEST_DATABASE_URL")
        if parsed.path.removeprefix("/") != "auth_test_ai_test":
            raise RuntimeError(
                "TEST_DATABASE_URL must target the auth_test_ai_test database"
            )


class ProductionConfig(BaseConfig):
    """Production configuration requiring an externally managed secret."""

    SECRET_KEY = os.getenv("SECRET_KEY")

    @classmethod
    def validate(cls, values: dict[str, object] | None = None) -> None:
        config = values or {
            "SECRET_KEY": cls.SECRET_KEY,
            "DATABASE_URL": cls.DATABASE_URL,
            "RATELIMIT_STORAGE_URI": cls.RATELIMIT_STORAGE_URI,
        }
        if not is_acceptable_production_secret(config.get("SECRET_KEY")):
            raise RuntimeError("A strong SECRET_KEY is required in production")
        validate_production_database_url(config.get("DATABASE_URL"))
        validate_production_rate_limit_storage(config.get("RATELIMIT_STORAGE_URI"))


CONFIGURATIONS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def is_acceptable_production_secret(value: object) -> bool:
    """Reject public, predictable, or manifestly weak production secrets."""
    if (
        not isinstance(value, str)
        or not MINIMUM_SECRET_LENGTH <= len(value) <= MAXIMUM_SECRET_LENGTH
    ):
        return False
    normalized = value.strip().casefold()
    placeholders = {
        DEMONSTRATION_SECRET.casefold(),
        "development-only-change-me",
        "development-only-replace-with-a-random-secret",
        "change-me",
        "changeme",
        "secret",
        "password",
    }
    if normalized in placeholders:
        return False
    if len(set(value)) == 1:
        return False
    predictable_fragments = ("replace_with", "replace-with", "example", "placeholder")
    if any(fragment in normalized for fragment in predictable_fragments):
        return False
    if normalized.isnumeric() or re.fullmatch(r"[0-9a-f]+", normalized):
        return False
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    if any(alphabet[index : index + 8] in normalized for index in range(19)):
        return False
    if _has_predominant_repeating_pattern(value):
        return False
    character_classes = sum(
        (
            any(character.islower() for character in value),
            any(character.isupper() for character in value),
            any(character.isdigit() for character in value),
            any(character in "-_" for character in value),
        )
    )
    return character_classes >= 3 and bool(re.fullmatch(r"[A-Za-z0-9_-]+", value))


def _has_predominant_repeating_pattern(value: str) -> bool:
    """Detect short repeated runs in an already length-bounded secret."""
    for pattern_length in range(1, min(8, len(value) // 3) + 1):
        for start in range(len(value) - (pattern_length * 3) + 1):
            pattern = value[start : start + pattern_length]
            end = start
            while value.startswith(pattern, end):
                end += pattern_length
            repeated_length = end - start
            if (
                repeated_length >= pattern_length * 3
                and repeated_length / len(value) >= 0.75
            ):
                return True
    return False


def validate_production_database_url(value: object) -> None:
    """Require the PostgreSQL driver installed and supported by this project."""
    if not isinstance(value, str) or not value:
        raise RuntimeError("A valid PostgreSQL DATABASE_URL is required in production")
    try:
        database_url = make_url(value)
        port = database_url.port
    except (ArgumentError, TypeError, ValueError):
        raise RuntimeError(
            "A valid PostgreSQL DATABASE_URL is required in production"
        ) from None
    if (
        database_url.drivername != PRODUCTION_DATABASE_DRIVER
        or not database_url.database
        or not database_url.database.strip()
        or port is not None
        and not 1 <= port <= 65535
    ):
        raise RuntimeError("A valid PostgreSQL DATABASE_URL is required in production")


def validate_production_rate_limit_storage(value: object) -> None:
    """Require a supported shared Redis store without disclosing its URI."""
    if not isinstance(value, str) or not value:
        raise RuntimeError(
            "A supported shared RATELIMIT_STORAGE_URI is required in production"
        )
    if value != value.strip() or any(
        character.isspace() or ord(character) < 32 or ord(character) == 127
        for character in value
    ):
        raise RuntimeError(
            "A supported shared RATELIMIT_STORAGE_URI is required in production"
        )
    try:
        parsed = urlsplit(value)
        hostname = unquote(parsed.hostname or "")
        port = parsed.port
    except (UnicodeError, ValueError):
        raise RuntimeError(
            "A supported shared RATELIMIT_STORAGE_URI is required in production"
        ) from None
    if (
        parsed.scheme.casefold() not in PRODUCTION_RATE_LIMIT_STORAGE_SCHEMES
        or not hostname
        or not hostname.strip()
        or any(
            character.isspace() or ord(character) < 32 or ord(character) == 127
            for character in hostname
        )
        or port is not None
        and not 1 <= port <= 65535
    ):
        raise RuntimeError(
            "A supported shared RATELIMIT_STORAGE_URI is required in production"
        )
