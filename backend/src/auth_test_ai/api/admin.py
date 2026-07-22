import uuid
from datetime import UTC, datetime

from flask import Blueprint, jsonify, request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from auth_test_ai.authorization import role_required
from auth_test_ai.csrf import require_csrf
from auth_test_ai.errors import ApiError
from auth_test_ai.extensions import db
from auth_test_ai.models import AuthenticationAttempt, User
from auth_test_ai.services.user_service import create_user

admin_blueprint = Blueprint("admin", __name__, url_prefix="/api/admin")


def _pagination() -> tuple[int, int]:
    try:
        page = int(request.args.get("page", "1"))
        limit = int(request.args.get("limit", "20"))
    except ValueError as error:
        raise ApiError("VALIDATION_ERROR", "Invalid pagination.", 400) from error
    if page < 1 or limit < 1 or limit > 100:
        raise ApiError("VALIDATION_ERROR", "Invalid pagination.", 400)
    return page, limit


@admin_blueprint.get("/users")
@role_required("ADMIN")
def list_users() -> tuple[object, int]:
    page, limit = _pagination()
    statement = select(User).order_by(User.created_at, User.id)
    active = request.args.get("isActive")
    if active is not None:
        if active not in {"true", "false"}:
            raise ApiError("VALIDATION_ERROR", "Invalid status filter.", 400)
        statement = statement.where(User.is_active.is_(active == "true"))
    page_result = db.paginate(statement, page=page, per_page=limit, error_out=False)
    return jsonify(
        items=[user.to_public_dict() for user in page_result.items],
        page=page,
        limit=limit,
        total=page_result.total,
    ), 200


@admin_blueprint.post("/users")
@require_csrf
@role_required("ADMIN")
def add_user() -> tuple[object, int]:
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise ApiError("VALIDATION_ERROR", "Invalid request data.", 400)
    try:
        user = create_user(
            first_name=payload.get("firstName"),
            last_name=payload.get("lastName"),
            login=payload.get("login"),
            password=payload.get("password"),
            role_names=tuple(payload.get("roles", ["USER"])),
        )
        db.session.commit()
    except LookupError as error:
        db.session.rollback()
        raise ApiError("LOGIN_ALREADY_EXISTS", "Login already exists.", 409) from error
    except (TypeError, ValueError) as error:
        db.session.rollback()
        raise ApiError("VALIDATION_ERROR", "Invalid request data.", 400) from error
    except IntegrityError as error:
        db.session.rollback()
        raise ApiError("LOGIN_ALREADY_EXISTS", "Login already exists.", 409) from error
    return jsonify(user=user.to_public_dict()), 201


@admin_blueprint.patch("/users/<uuid:user_id>/status")
@require_csrf
@role_required("ADMIN")
def update_user_status(user_id: uuid.UUID) -> tuple[object, int]:
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not isinstance(payload.get("isActive"), bool):
        raise ApiError("VALIDATION_ERROR", "Invalid request data.", 400)
    user = db.session.get(User, user_id)
    if user is None:
        raise ApiError("RESOURCE_NOT_FOUND", "Resource not found.", 404)
    user.is_active = payload["isActive"]
    db.session.commit()
    return jsonify(user=user.to_public_dict()), 200


@admin_blueprint.get("/auth-attempts")
@role_required("ADMIN")
def list_authentication_attempts() -> tuple[object, int]:
    page, limit = _pagination()
    statement = select(AuthenticationAttempt).order_by(
        AuthenticationAttempt.created_at.desc(), AuthenticationAttempt.id
    )
    success = request.args.get("success")
    if success is not None:
        if success not in {"true", "false"}:
            raise ApiError("VALIDATION_ERROR", "Invalid success filter.", 400)
        statement = statement.where(
            AuthenticationAttempt.success.is_(success == "true")
        )
    user_id = request.args.get("user_id")
    if user_id:
        try:
            statement = statement.where(
                AuthenticationAttempt.user_id == uuid.UUID(user_id)
            )
        except ValueError as error:
            raise ApiError("VALIDATION_ERROR", "Invalid user filter.", 400) from error
    since = request.args.get("date_from") or request.args.get("date")
    until = request.args.get("date_to")
    if since:
        try:
            parsed_since = datetime.fromisoformat(since)
            if parsed_since.tzinfo is None:
                parsed_since = parsed_since.replace(tzinfo=UTC)
            statement = statement.where(
                AuthenticationAttempt.created_at >= parsed_since
            )
        except ValueError as error:
            raise ApiError("VALIDATION_ERROR", "Invalid date filter.", 400) from error
    if until:
        try:
            parsed_until = datetime.fromisoformat(until)
            if parsed_until.tzinfo is None:
                parsed_until = parsed_until.replace(tzinfo=UTC)
            statement = statement.where(
                AuthenticationAttempt.created_at <= parsed_until
            )
        except ValueError as error:
            raise ApiError("VALIDATION_ERROR", "Invalid date filter.", 400) from error
    page_result = db.paginate(statement, page=page, per_page=limit, error_out=False)
    return jsonify(
        items=[item.to_audit_dict() for item in page_result.items],
        page=page,
        limit=limit,
        total=page_result.total,
    ), 200
