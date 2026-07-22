from pathlib import Path

import pytest
from flask import Flask
from flask_migrate import downgrade, upgrade
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import BYTEA, INTEGER, TIMESTAMP, VARCHAR

from auth_test_ai.extensions import db


@pytest.mark.integration
def test_initial_migration_tables_are_present(app: Flask, clean_database: None) -> None:
    del clean_database
    with app.app_context():
        tables = set(inspect(db.engine).get_table_names())
    assert {
        "users",
        "roles",
        "user_roles",
        "authentication_attempts",
        "server_sessions",
    } <= tables


@pytest.mark.integration
def test_session_schema_matches_flask_session_model(
    app: Flask, clean_database: None
) -> None:
    del clean_database
    with app.app_context():
        inspector = inspect(db.engine)
        table_name = app.config["SESSION_SQLALCHEMY_TABLE"]
        assert table_name == "server_sessions"
        reflected_columns = {
            column["name"]: column for column in inspector.get_columns(table_name)
        }
        indexes = {
            index["name"]
            for index in inspector.get_indexes(table_name)
            if not index.get("duplicates_constraint")
        }
        unique_columns = {
            tuple(item["column_names"])
            for item in inspector.get_unique_constraints(table_name)
        }
        model = app.session_interface.sql_session_model.__table__
        expected = {
            "id": (INTEGER, None, False),
            "session_id": (VARCHAR, 255, True),
            "data": (BYTEA, None, True),
            "expiry": (TIMESTAMP, None, True),
        }
        assert model.name == table_name
        assert (
            set(reflected_columns)
            == set(expected)
            == {column.name for column in model.columns}
        )
        for name, (type_class, length, nullable) in expected.items():
            reflected = reflected_columns[name]
            assert isinstance(reflected["type"], type_class)
            assert getattr(reflected["type"], "length", None) == length
            assert reflected["nullable"] is nullable
            runtime = model.columns[name]
            assert getattr(runtime.type, "length", None) == length
            assert runtime.nullable is nullable
        assert reflected_columns["expiry"]["type"].timezone is False
        assert model.columns["expiry"].type.timezone is False
        assert inspector.get_pk_constraint(table_name)["constrained_columns"] == ["id"]
        assert [column.name for column in model.primary_key.columns] == ["id"]
        assert ("session_id",) in unique_columns
        assert model.columns["session_id"].unique is True
        assert indexes == set()


@pytest.mark.integration
def test_alembic_empty_upgrade_downgrade_and_second_upgrade(app: Flask) -> None:
    assert (
        app.config["SQLALCHEMY_DATABASE_URI"].rsplit("/", 1)[-1] == "auth_test_ai_test"
    )
    with app.app_context():
        migrations = str(Path(__file__).parents[2] / "migrations")
        try:
            downgrade(directory=migrations, revision="base")
            assert "users" not in inspect(db.engine).get_table_names()
            upgrade(directory=migrations)
            assert "users" in inspect(db.engine).get_table_names()
            downgrade(directory=migrations, revision="base")
            assert "users" not in inspect(db.engine).get_table_names()
            upgrade(directory=migrations)
            assert "users" in inspect(db.engine).get_table_names()
        finally:
            upgrade(directory=migrations)
