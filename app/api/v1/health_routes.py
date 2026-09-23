from flask import Blueprint, jsonify


api_health_bp = Blueprint(
    "api_health",
    __name__,
)


@api_health_bp.get("/health")
def health_check():
    return jsonify({
        "status": "ok",
        "service": "app_lecturas_emax",
        "api_version": "v1",
    }), 200
