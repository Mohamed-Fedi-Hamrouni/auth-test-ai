import re
from copy import deepcopy
from pathlib import Path

import pytest
import yaml
from flask import Flask
from scripts.validate_openapi import EXPECTED_OPERATIONS, validate

from auth_test_ai import create_app
from auth_test_ai.api.admin import admin_blueprint
from auth_test_ai.api.auth import auth_blueprint
from auth_test_ai.api.docs import docs_blueprint
from auth_test_ai.api.health import health_blueprint
from auth_test_ai.config import DevelopmentConfig, ProductionConfig, TestingConfig
from auth_test_ai.errors import register_error_handlers

SPECIFICATION = Path(__file__).parents[3] / "docs/openapi/auth-test-ai.openapi.yaml"


def docs_app(enabled: bool) -> Flask:
    application = Flask(__name__)
    application.config.update(TESTING=True, API_DOCS_ENABLED=enabled)
    application.register_blueprint(docs_blueprint)
    register_error_handlers(application)
    return application


def load_specification() -> dict[str, object]:
    document = yaml.safe_load(SPECIFICATION.read_text(encoding="utf-8"))
    assert isinstance(document, dict)
    return document


def operation_skeleton(path: str) -> str:
    path = re.sub(r"<(?:[^:>]+:)?[^>]+>", "{}", path)
    return re.sub(r"{[^}]+}", "{}", path)


@pytest.mark.unit
def test_openapi_endpoint_serves_parseable_31_contract() -> None:
    response = docs_app(True).test_client().get("/api/openapi.yaml")
    document = yaml.safe_load(response.get_data(as_text=True))
    assert response.status_code == 200
    assert response.mimetype in {"application/yaml", "application/openapi+yaml"}
    assert document["openapi"].startswith("3.1.")
    assert document["servers"][0] == {
        "url": "/",
        "description": "Current application origin",
    }
    assert document["servers"][1]["url"] == "http://localhost:5000"


@pytest.mark.unit
def test_swagger_ui_uses_same_origin_credentials_without_embedding_secrets() -> None:
    response = docs_app(True).test_client().get("/api/docs")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "/api/openapi.yaml" in html
    assert 'request.credentials = "same-origin"' in html
    assert "swagger-ui-dist@5.17.14" in html
    content_security_policy = response.headers["Content-Security-Policy"]
    nonce_match = re.search(r"'nonce-([^']+)'", content_security_policy)
    assert nonce_match is not None
    assert f'nonce="{nonce_match.group(1)}"' in html
    assert "script-src https://cdn.jsdelivr.net" in content_security_policy
    assert "style-src https://cdn.jsdelivr.net" in content_security_policy
    assert "connect-src 'self'" in content_security_policy
    assert "object-src 'none'" in content_security_policy
    assert "latest" not in html.casefold()
    assert set(re.findall(r"https://[^/\s\"']+", html)) == {"https://cdn.jsdelivr.net"}
    for forbidden in (
        "auth_test_ai_session=",
        "csrfToken:",
        "fictitious-password-from-environment",
        "DATABASE_URL",
        "SECRET_KEY",
    ):
        assert forbidden not in html


@pytest.mark.unit
def test_docs_environment_defaults_and_disabled_json_404() -> None:
    assert DevelopmentConfig.API_DOCS_ENABLED is True
    assert TestingConfig.API_DOCS_ENABLED is True
    assert ProductionConfig.API_DOCS_ENABLED is False
    client = docs_app(False).test_client()
    for path in ("/api/docs", "/api/openapi.yaml"):
        response = client.get(path)
        assert response.status_code == 404
        assert response.get_json() == {
            "error": {
                "code": "RESOURCE_NOT_FOUND",
                "message": "Resource not found.",
                "details": {},
            }
        }


@pytest.mark.unit
def test_explicit_production_enablement_with_extensions_isolated(
    monkeypatch: pytest.MonkeyPatch, mocker
) -> None:
    mocker.patch("auth_test_ai.init_extensions")
    monkeypatch.setenv("SECRET_KEY", "qB7_mN2-Zx9Lp4_Vc8Ks1-Wd6Yr3_Ht5")
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql+psycopg://service.invalid/application"
    )
    monkeypatch.setenv("RATELIMIT_STORAGE_URI", "redis://service.invalid/0")
    monkeypatch.setenv("API_DOCS_ENABLED", "true")
    client = create_app("production").test_client()
    assert client.get("/api/docs").status_code == 200
    assert client.get("/api/openapi.yaml").status_code == 200


@pytest.mark.unit
def test_docs_blueprint_serving_does_not_query_external_services(mocker) -> None:
    database_connect = mocker.patch("sqlalchemy.engine.Engine.connect")
    redis_connect = mocker.patch("redis.Redis.from_url")
    client = docs_app(True).test_client()
    assert client.get("/api/docs").status_code == 200
    assert client.get("/api/openapi.yaml").status_code == 200
    database_connect.assert_not_called()
    redis_connect.assert_not_called()


@pytest.mark.unit
def test_contract_security_and_public_field_consistency() -> None:
    document = load_specification()
    schemas = document["components"]["schemas"]
    public_user = set(schemas["PublicUser"]["properties"])
    assert public_user == {"id", "firstName", "lastName", "login", "roles", "isActive"}
    text = SPECIFICATION.read_text(encoding="utf-8")
    for forbidden in (
        "password_hash",
        "internal_failure_reason",
        "ip_address_hash",
        "session_id",
    ):
        assert forbidden not in text
    assert "Invalid login or password." in text
    assert "HttpOnly" in text and "PostgreSQL" in text
    csrf_operations = {
        ("/api/auth/login", "post"),
        ("/api/auth/logout", "post"),
        ("/api/admin/users", "post"),
        ("/api/admin/users/{id}/status", "patch"),
    }
    for path_name, path_item in document["paths"].items():
        for method, operation in path_item.items():
            refs = {
                parameter.get("$ref")
                for parameter in operation.get("parameters", [])
                if isinstance(parameter, dict)
            }
            has_csrf = "#/components/parameters/CsrfHeader" in refs
            assert has_csrf == ((path_name, method) in csrf_operations)


@pytest.mark.unit
def test_openapi_operations_match_real_blueprint_rules() -> None:
    application = Flask(__name__)
    for blueprint in (
        health_blueprint,
        auth_blueprint,
        admin_blueprint,
        docs_blueprint,
    ):
        application.register_blueprint(blueprint)
    actual_operations = {
        (operation_skeleton(rule.rule), method.casefold())
        for rule in application.url_map.iter_rules()
        if rule.endpoint != "static" and not rule.endpoint.startswith("api_docs.")
        for method in rule.methods
        if method not in {"HEAD", "OPTIONS"}
    }
    document = load_specification()
    openapi_operations = {
        (operation_skeleton(path), method)
        for path, path_item in document["paths"].items()
        for method in path_item
        if method in {"get", "post", "put", "patch", "delete"}
    }
    expected_operations = {
        (operation_skeleton(path), method) for path, method in EXPECTED_OPERATIONS
    }
    assert actual_operations == openapi_operations == expected_operations


@pytest.mark.unit
def test_request_schema_constraints_match_backend_validation() -> None:
    schemas = load_specification()["components"]["schemas"]
    login = schemas["LoginRequest"]["properties"]["login"]
    assert login["type"] == "string"
    assert login["minLength"] == 1
    assert login["maxLength"] == 100
    assert re.search(login["pattern"], "   ") is None
    assert re.search(login["pattern"], "sample.user") is not None
    assert "trim" in login["description"].casefold()
    login_password = schemas["LoginRequest"]["properties"]["password"]
    assert (login_password["minLength"], login_password["maxLength"]) == (1, 128)
    assert login_password["writeOnly"] is True

    create_user = schemas["CreateUserRequest"]
    assert set(create_user["required"]) == {
        "firstName",
        "lastName",
        "login",
        "password",
    }
    for name in ("firstName", "lastName", "login"):
        field = create_user["properties"][name]
        assert field["minLength"] == 1
        assert field["maxLength"] == 100
        assert re.search(field["pattern"], "   ") is None
        assert "trim" in field["description"].casefold()
    password = create_user["properties"]["password"]
    assert (password["minLength"], password["maxLength"]) == (15, 128)
    assert create_user["properties"]["roles"]["items"]["enum"] == [
        "USER",
        "ADMIN",
    ]


@pytest.mark.unit
def test_validator_allows_only_intentional_sensitive_properties() -> None:
    validate(load_specification())


@pytest.mark.unit
@pytest.mark.parametrize("schema_name", ["LoginRequest", "CreateUserRequest"])
def test_validator_rejects_other_sensitive_request_properties(
    schema_name: str,
) -> None:
    document = deepcopy(load_specification())
    document["components"]["schemas"][schema_name]["properties"]["rawPassword"] = {
        "type": "string"
    }
    with pytest.raises(AssertionError, match="Sensitive property 'rawPassword'"):
        validate(document)
