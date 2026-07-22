from flask import Blueprint, jsonify

health_blueprint = Blueprint("health", __name__, url_prefix="/api")


@health_blueprint.get("/health")
def health() -> tuple[object, int]:
    """Return a stable application health response."""
    return jsonify(status="ok"), 200
