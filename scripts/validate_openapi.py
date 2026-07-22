#!/usr/bin/env python3
"""Validate the AuthTest AI OpenAPI contract without network access."""

from pathlib import Path
from typing import Any

import yaml

SPECIFICATION = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "openapi"
    / "auth-test-ai.openapi.yaml"
)

EXPECTED_OPERATIONS = {
    ("/api/health", "get"): {"200", "500"},
    ("/api/auth/csrf", "get"): {"200", "500"},
    ("/api/auth/login", "post"): {"200", "400", "401", "413", "429", "500"},
    ("/api/auth/logout", "post"): {"204", "400", "401", "500"},
    ("/api/auth/me", "get"): {"200", "401", "500"},
    ("/api/admin/users", "get"): {"200", "400", "401", "403", "500"},
    ("/api/admin/users", "post"): {
        "201",
        "400",
        "401",
        "403",
        "409",
        "413",
        "500",
    },
    ("/api/admin/users/{id}/status", "patch"): {
        "200",
        "400",
        "401",
        "403",
        "404",
        "413",
        "500",
    },
    ("/api/admin/auth-attempts", "get"): {
        "200",
        "400",
        "401",
        "403",
        "500",
    },
}
REQUIRED_SCHEMAS = {
    "HealthResponse",
    "CsrfResponse",
    "LoginRequest",
    "LoginResponse",
    "PublicUser",
    "UserListResponse",
    "CreateUserRequest",
    "UpdateUserStatusRequest",
    "AuthenticationAttempt",
    "AuthenticationAttemptListResponse",
    "Pagination",
    "ErrorEnvelope",
}
SENSITIVE_FIELDS = {
    "password",
    "password_hash",
    "passwordHash",
    "rawPassword",
    "internal_failure_reason",
    "internalFailureReason",
    "ip_address",
    "ipAddress",
    "ip_address_hash",
    "ipAddressHash",
    "session_id",
    "sessionId",
    "cookie",
    "csrf_token",
    "csrfSecret",
    "csrf_secret",
    "csrfToken",
}
ALLOWED_SENSITIVE_PROPERTIES = {
    ("LoginRequest", "password"),
    ("CreateUserRequest", "password"),
    ("CsrfResponse", "csrfToken"),
}
CSRF_OPERATIONS = {
    ("/api/auth/login", "post"),
    ("/api/auth/logout", "post"),
    ("/api/admin/users", "post"),
    ("/api/admin/users/{id}/status", "patch"),
}


def load_specification() -> dict[str, Any]:
    """Load the canonical YAML document."""
    document = yaml.safe_load(SPECIFICATION.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise AssertionError("OpenAPI document must be a mapping")
    return document


def _resolve_local_reference(document: dict[str, Any], reference: str) -> Any:
    if not reference.startswith("#/"):
        raise AssertionError(f"Only local references are allowed: {reference}")
    target: Any = document
    for part in reference[2:].split("/"):
        target = target[part.replace("~1", "/").replace("~0", "~")]
    return target


def _walk_references(document: dict[str, Any], value: Any) -> None:
    if isinstance(value, dict):
        if "$ref" in value:
            _resolve_local_reference(document, value["$ref"])
        for child in value.values():
            _walk_references(document, child)
    elif isinstance(value, list):
        for child in value:
            _walk_references(document, child)


def _schema_property_names(value: Any) -> list[str]:
    names: list[str] = []
    if isinstance(value, dict):
        properties = value.get("properties")
        if isinstance(properties, dict):
            names.extend(str(name) for name in properties)
        for child in value.values():
            names.extend(_schema_property_names(child))
    elif isinstance(value, list):
        for child in value:
            names.extend(_schema_property_names(child))
    return names


def _validate_sensitive_schema_properties(schemas: dict[str, Any]) -> None:
    for schema_name, schema in schemas.items():
        for property_name in _schema_property_names(schema):
            if (
                property_name in SENSITIVE_FIELDS
                and (schema_name, property_name) not in ALLOWED_SENSITIVE_PROPERTIES
            ):
                raise AssertionError(
                    f"Sensitive property {property_name!r} appears in {schema_name}"
                )


def validate(document: dict[str, Any]) -> None:
    """Validate project-specific OpenAPI and security invariants."""
    if document.get("openapi") != "3.1.0":
        raise AssertionError("The specification must use OpenAPI 3.1.0")
    servers = document.get("servers")
    if not isinstance(servers, list) or not servers or servers[0].get("url") != "/":
        raise AssertionError("The default OpenAPI server must use the current origin")
    operations = {
        (path, method): operation
        for path, path_item in document["paths"].items()
        for method, operation in path_item.items()
        if method in {"get", "post", "put", "patch", "delete"}
    }
    if set(operations) != set(EXPECTED_OPERATIONS):
        raise AssertionError("Documented operations differ from implemented API routes")
    for key, expected_statuses in EXPECTED_OPERATIONS.items():
        actual = set(operations[key]["responses"])
        if actual != expected_statuses:
            raise AssertionError(f"Response statuses differ for {key}: {actual}")
    schemas = document["components"]["schemas"]
    if not REQUIRED_SCHEMAS <= set(schemas):
        raise AssertionError("A required component schema is missing")
    _validate_sensitive_schema_properties(schemas)
    for key, operation in operations.items():
        header_names = {
            parameter.get("name")
            for parameter in operation.get("parameters", [])
            if isinstance(parameter, dict) and "$ref" not in parameter
        }
        header_refs = {
            parameter.get("$ref") for parameter in operation.get("parameters", [])
        }
        has_csrf = "X-CSRFToken" in header_names or (
            "#/components/parameters/CsrfHeader" in header_refs
        )
        if has_csrf != (key in CSRF_OPERATIONS):
            raise AssertionError(f"Incorrect CSRF documentation for {key}")
        if key[1] == "get" and has_csrf:
            raise AssertionError(f"GET operation incorrectly requires CSRF: {key}")
    _walk_references(document, document)


def main() -> None:
    document = load_specification()
    validate(document)
    print(f"OpenAPI validation passed: {len(EXPECTED_OPERATIONS)} operations")


if __name__ == "__main__":
    main()
