from flask import Blueprint, current_app, g, jsonify, make_response, request

from auth_test_ai.authorization import login_required
from auth_test_ai.csrf import issue_csrf_token, require_csrf
from auth_test_ai.errors import ApiError, error_response
from auth_test_ai.extensions import db, limiter
from auth_test_ai.models import AuthenticationFailureReason
from auth_test_ai.services.audit_service import record_attempt
from auth_test_ai.services.authentication_service import authenticate
from auth_test_ai.services.session_service import create_user_session, destroy_session

auth_blueprint = Blueprint("auth", __name__, url_prefix="/api/auth")


def _handle_login_rate_limit(_limit: object) -> tuple[object, int]:
    payload = request.get_json(silent=True)
    attempted_login = payload.get("login", "") if isinstance(payload, dict) else ""
    if not isinstance(attempted_login, str):
        attempted_login = ""
    attempted_login = attempted_login[:100]
    record_attempt(
        user=None,
        attempted_login=attempted_login,
        success=False,
        reason=AuthenticationFailureReason.RATE_LIMITED,
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string,
    )
    db.session.commit()
    return error_response(ApiError("RATE_LIMITED", "Too many requests.", 429))


@auth_blueprint.get("/csrf")
def csrf_token() -> tuple[object, int]:
    return jsonify(csrfToken=issue_csrf_token()), 200


@auth_blueprint.post("/login")
@require_csrf
@limiter.limit(
    lambda: current_app.config["LOGIN_RATE_LIMIT"],
    on_breach=_handle_login_rate_limit,
)
def login() -> tuple[object, int]:
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise ApiError("VALIDATION_ERROR", "Invalid request data.", 400)
    login_value = payload.get("login")
    password = payload.get("password")
    details = {}
    if not isinstance(login_value, str) or not login_value.strip():
        details["login"] = "Login is required."
    elif len(login_value) > 100:
        details["login"] = "Login must contain at most 100 characters."
    if not isinstance(password, str) or not password:
        details["password"] = "Password is required."
    elif len(password) > 128:
        details["password"] = "Password must contain at most 128 characters."
    if details:
        raise ApiError("VALIDATION_ERROR", "Invalid request data.", 400, details)
    result = authenticate(
        login=login_value,
        password=password,
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string,
    )
    if not result.authenticated or result.user is None:
        raise ApiError("AUTH_INVALID_CREDENTIALS", "Invalid login or password.", 401)
    create_user_session(result.user.id)
    return (
        jsonify(
            user=result.user.to_public_dict(),
            message=f"Welcome {result.user.first_name} {result.user.last_name}",
        ),
        200,
    )


@auth_blueprint.post("/logout")
@require_csrf
@login_required
def logout() -> tuple[object, int]:
    destroy_session()
    response = make_response("", 204)
    response.delete_cookie(
        current_app.config["SESSION_COOKIE_NAME"],
        httponly=current_app.config["SESSION_COOKIE_HTTPONLY"],
        secure=current_app.config["SESSION_COOKIE_SECURE"],
        samesite=current_app.config["SESSION_COOKIE_SAMESITE"],
    )
    return response, 204


@auth_blueprint.get("/me")
@login_required
def me() -> tuple[object, int]:
    return jsonify(user=g.current_user.to_public_dict()), 200
