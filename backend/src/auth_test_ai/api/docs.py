import secrets
from pathlib import Path

from flask import (
    Blueprint,
    Response,
    current_app,
    make_response,
    render_template_string,
)

docs_blueprint = Blueprint("api_docs", __name__, url_prefix="/api")

OPENAPI_PATH = (
    Path(__file__).resolve().parents[4]
    / "docs"
    / "openapi"
    / "auth-test-ai.openapi.yaml"
)

SWAGGER_UI_VERSION = "5.17.14"
SWAGGER_UI_TEMPLATE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>AuthTest AI API documentation</title>
    <link rel="stylesheet" href="{{ asset_base }}/swagger-ui.css">
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="{{ asset_base }}/swagger-ui-bundle.js">
    </script>
    <script nonce="{{ nonce }}">
      window.ui = SwaggerUIBundle({
        url: {{ spec_url|tojson }},
        dom_id: "#swagger-ui",
        deepLinking: true,
        displayRequestDuration: true,
        requestInterceptor: function (request) {
          request.credentials = "same-origin";
          return request;
        }
      });
    </script>
  </body>
</html>
"""


def _docs_enabled() -> bool:
    return bool(current_app.config["API_DOCS_ENABLED"])


@docs_blueprint.get("/openapi.yaml")
def openapi_specification() -> Response:
    """Serve the repository's canonical, static OpenAPI specification."""
    if not _docs_enabled():
        current_app.aborter(404)
    return Response(
        OPENAPI_PATH.read_bytes(),
        status=200,
        content_type="application/yaml; charset=utf-8",
    )


@docs_blueprint.get("/docs")
def swagger_ui() -> Response:
    """Serve a same-origin Swagger UI configured for browser-managed cookies."""
    if not _docs_enabled():
        current_app.aborter(404)
    nonce = secrets.token_urlsafe(24)
    response = make_response(
        render_template_string(
            SWAGGER_UI_TEMPLATE,
            asset_base=(
                "https://cdn.jsdelivr.net/npm/swagger-ui-dist@" + SWAGGER_UI_VERSION
            ),
            nonce=nonce,
            spec_url="/api/openapi.yaml",
        )
    )
    response.headers["Content-Security-Policy"] = "; ".join(
        (
            "default-src 'none'",
            f"script-src https://cdn.jsdelivr.net 'nonce-{nonce}'",
            "style-src https://cdn.jsdelivr.net",
            "img-src 'self' data:",
            "connect-src 'self'",
            "object-src 'none'",
            "base-uri 'none'",
            "frame-ancestors 'none'",
        )
    )
    return response
