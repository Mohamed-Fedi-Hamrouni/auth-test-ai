import os

from flask import Flask

from auth_test_ai.api.admin import admin_blueprint
from auth_test_ai.api.auth import auth_blueprint
from auth_test_ai.api.docs import docs_blueprint
from auth_test_ai.api.health import health_blueprint
from auth_test_ai.cli import register_cli
from auth_test_ai.config import (
    CONFIGURATIONS,
    ENVIRONMENT_VARIABLE,
    ProductionConfig,
    TestingConfig,
    bool_env,
)
from auth_test_ai.errors import register_error_handlers
from auth_test_ai.extensions import init_extensions


def create_app(config: str | None = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    if config is not None and not isinstance(config, str):
        raise TypeError("create_app accepts only an explicit environment name")
    selected = config if config is not None else os.getenv(ENVIRONMENT_VARIABLE)
    if selected is None:
        raise RuntimeError(
            f"{ENVIRONMENT_VARIABLE} must be set to development, testing, or production"
        )
    if isinstance(selected, str):
        config_class = CONFIGURATIONS.get(selected)
        if config_class is None:
            raise RuntimeError(f"Unknown application configuration: {selected}")
        app.config.from_object(config_class)
        app.config["ENVIRONMENT"] = selected
        app.config["API_DOCS_ENABLED"] = bool_env(
            "API_DOCS_ENABLED", bool(app.config["API_DOCS_ENABLED"])
        )
        if issubclass(config_class, ProductionConfig):
            app.config.update(
                SECRET_KEY=os.getenv("SECRET_KEY"),
                DATABASE_URL=os.getenv("DATABASE_URL"),
                SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL"),
                RATELIMIT_STORAGE_URI=os.getenv("RATELIMIT_STORAGE_URI"),
            )
            config_class.validate(app.config)
        elif issubclass(config_class, TestingConfig):
            config_class.validate(app.config)
    init_extensions(app)
    from auth_test_ai import models  # noqa: F401

    app.register_blueprint(health_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(docs_blueprint)
    register_error_handlers(app)
    register_cli(app)
    return app
