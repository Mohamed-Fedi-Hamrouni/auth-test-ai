import unicodedata

from sqlalchemy import select

from auth_test_ai.extensions import db
from auth_test_ai.models import Role, User
from auth_test_ai.services.password_service import hash_password


def normalize_login(login: str) -> str:
    return unicodedata.normalize("NFKC", login.strip()).casefold()


def user_lookup_statement(login: str, *, for_update: bool = False):
    statement = select(User).where(User.login_normalized == normalize_login(login))
    return statement.with_for_update() if for_update else statement


def get_user_by_login(login: str, *, for_update: bool = False) -> User | None:
    return db.session.scalar(user_lookup_statement(login, for_update=for_update))


def ensure_roles() -> dict[str, Role]:
    roles = {}
    for name, description in (
        ("USER", "Standard application user"),
        ("ADMIN", "Application administrator"),
    ):
        role = db.session.scalar(select(Role).where(Role.name == name))
        if role is None:
            role = Role(name=name, description=description)
            db.session.add(role)
            db.session.flush()
        roles[name] = role
    return roles


def create_user(
    *,
    first_name: str,
    last_name: str,
    login: str,
    password: str,
    role_names: tuple[str, ...] = ("USER",),
    is_active: bool = True,
) -> User:
    if not all(isinstance(value, str) for value in (first_name, last_name, login)):
        raise ValueError("Invalid user fields")
    if not isinstance(password, str):
        raise ValueError("Invalid password")
    normalized = normalize_login(login)
    if not normalized or len(normalized) > 100:
        raise ValueError("Invalid login")
    if not first_name.strip() or len(first_name.strip()) > 100:
        raise ValueError("Invalid first name")
    if not last_name.strip() or len(last_name.strip()) > 100:
        raise ValueError("Invalid last name")
    if get_user_by_login(login) is not None:
        raise LookupError("Login already exists")
    roles = ensure_roles()
    if any(name not in roles for name in role_names):
        raise ValueError("Invalid role")
    user = User(
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        login=login.strip(),
        login_normalized=normalized,
        password_hash=hash_password(password),
        is_active=is_active,
        roles=[roles[name] for name in role_names],
    )
    db.session.add(user)
    db.session.flush()
    return user
