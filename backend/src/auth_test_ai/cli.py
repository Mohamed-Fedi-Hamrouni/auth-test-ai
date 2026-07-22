import os

import click
from flask import Flask
from sqlalchemy import select

from auth_test_ai.extensions import db
from auth_test_ai.models import User
from auth_test_ai.services.user_service import (
    create_user,
    ensure_roles,
    normalize_login,
)

SEED_USERS = (
    ("ADMIN", "Development", "Admin", "dev.admin", ("USER", "ADMIN"), True),
    ("USER_ONE", "Development", "User One", "dev.user1", ("USER",), True),
    ("USER_TWO", "Development", "User Two", "dev.user2", ("USER",), True),
    ("INACTIVE", "Inactive", "User", "dev.inactive", ("USER",), False),
    ("LOCKOUT", "Lockout", "User", "dev.lockout", ("USER",), True),
)


def register_cli(app: Flask) -> None:
    @app.cli.command("seed-dev-users")
    def seed_dev_users() -> None:
        """Create development roles and synthetic users idempotently."""
        if app.config.get("ENVIRONMENT") == "production":
            raise click.ClickException("Development seed is disabled in production.")
        if os.getenv("ALLOW_DEV_SEED", "").casefold() != "true":
            raise click.ClickException("ALLOW_DEV_SEED=true is required.")
        variable_names = [f"SEED_{prefix}_PASSWORD" for prefix, *_ in SEED_USERS]
        missing = [name for name in variable_names if not os.getenv(name)]
        if missing:
            raise click.ClickException(
                "Missing required environment variables: " + ", ".join(missing)
            )
        ensure_roles()
        for prefix, first_name, last_name, login, roles, active in SEED_USERS:
            existing = db.session.scalar(
                select(User).where(User.login_normalized == normalize_login(login))
            )
            if existing is None:
                create_user(
                    first_name=first_name,
                    last_name=last_name,
                    login=login,
                    password=os.environ[f"SEED_{prefix}_PASSWORD"],
                    role_names=roles,
                    is_active=active,
                )
        db.session.commit()
        click.echo("Development users are ready.")
