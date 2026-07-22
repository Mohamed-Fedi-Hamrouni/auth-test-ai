from typing import Any

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException, RequestEntityTooLarge


class ApiError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


def error_response(error: ApiError) -> tuple[object, int]:
    return (
        jsonify(
            error={
                "code": error.code,
                "message": error.message,
                "details": error.details,
            }
        ),
        error.status_code,
    )


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(ApiError)
    def handle_api_error(error: ApiError) -> tuple[object, int]:
        return error_response(error)

    @app.errorhandler(RequestEntityTooLarge)
    def handle_oversized_request(error: RequestEntityTooLarge) -> tuple[object, int]:
        del error
        return error_response(
            ApiError("VALIDATION_ERROR", "Request body too large.", 413)
        )

    @app.errorhandler(429)
    def handle_rate_limit(error: HTTPException) -> tuple[object, int]:
        del error
        return error_response(ApiError("RATE_LIMITED", "Too many requests.", 429))

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException) -> tuple[object, int]:
        return error_response(
            ApiError("RESOURCE_NOT_FOUND", "Resource not found.", error.code or 500)
        )

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception) -> tuple[object, int]:
        if app.testing:
            raise error
        app.logger.error("Unhandled API error: %s", type(error).__name__)
        return error_response(ApiError("INTERNAL_ERROR", "Internal server error.", 500))
