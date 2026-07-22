from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy declarative model base."""


db = SQLAlchemy(model_class=Base)
migrate = Migrate()
server_session = Session()
limiter = Limiter(key_func=get_remote_address)


def init_extensions(app: Flask) -> None:
    """Initialize extensions without binding them at import time."""
    db.init_app(app)
    app.config["SESSION_SQLALCHEMY"] = db
    migrate.init_app(app, db)
    server_session.init_app(app)
    session_model = app.session_interface.sql_session_model
    session_model.__repr__ = lambda record: f"<ServerSession id={record.id}>"
    limiter.init_app(app)
