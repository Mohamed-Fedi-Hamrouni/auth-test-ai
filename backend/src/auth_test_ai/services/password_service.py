from dataclasses import dataclass
from functools import lru_cache

from argon2 import PasswordHasher, Type
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from flask import current_app


@dataclass(frozen=True)
class PasswordPolicyError:
    code: str
    message: str


def validate_password_policy(password: object) -> list[PasswordPolicyError]:
    if not isinstance(password, str):
        return [PasswordPolicyError("PASSWORD_TYPE", "Password must be a string.")]
    errors = []
    if len(password) < 15:
        errors.append(
            PasswordPolicyError(
                "PASSWORD_TOO_SHORT", "Password must contain at least 15 characters."
            )
        )
    if len(password) > 128:
        errors.append(
            PasswordPolicyError(
                "PASSWORD_TOO_LONG", "Password must contain at most 128 characters."
            )
        )
    return errors


def _hasher() -> PasswordHasher:
    return PasswordHasher(
        time_cost=current_app.config["ARGON2_TIME_COST"],
        memory_cost=current_app.config["ARGON2_MEMORY_COST"],
        parallelism=current_app.config["ARGON2_PARALLELISM"],
        type=Type.ID,
    )


@lru_cache(maxsize=8)
def _dummy_hash_for_parameters(
    time_cost: int, memory_cost: int, parallelism: int
) -> str:
    hasher = PasswordHasher(
        time_cost=time_cost,
        memory_cost=memory_cost,
        parallelism=parallelism,
        type=Type.ID,
    )
    return hasher.hash("fixed-dummy-password-never-used-for-authentication")


def dummy_password_hash() -> str:
    """Return one cached Argon2id dummy hash for the active cost parameters."""
    return _dummy_hash_for_parameters(
        current_app.config["ARGON2_TIME_COST"],
        current_app.config["ARGON2_MEMORY_COST"],
        current_app.config["ARGON2_PARALLELISM"],
    )


def hash_password(password: str) -> str:
    errors = validate_password_policy(password)
    if errors:
        raise ValueError(errors)
    return _hasher().hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _hasher().verify(password_hash, password)
    except (VerifyMismatchError, InvalidHashError):
        return False


def needs_rehash(password_hash: str) -> bool:
    try:
        return _hasher().check_needs_rehash(password_hash)
    except InvalidHashError:
        return True
