from flask import Flask

from auth_test_ai.api.health import health_blueprint
from auth_test_ai.config import Config
from auth_test_ai.extensions import init_extensions


def create_app(config: type[Config] = Config) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config)
    init_extensions(app)
    app.register_blueprint(health_blueprint)
    return app

