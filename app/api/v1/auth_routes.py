from flask import Blueprint, jsonify, request, session
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)

from app.services.auth_service import authenticate_user


api_auth_bp = Blueprint(
    "api_auth",
    __name__,
    url_prefix="/auth",
)


@api_auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}

    resultado = authenticate_user(
        nombre=data.get("nombre"),
        contrasena=data.get("contrasena"),
    )

    if not resultado["ok"]:
        status_codes = {
            "VALIDATION_ERROR": 400,
            "INVALID_CREDENTIALS": 401,
        }

        return jsonify(resultado), status_codes.get(
            resultado["code"],
            500,
        )

    user = resultado.pop("user")

    login_user(
        user,
        remember=False,
    )

    return jsonify(resultado), 200

@api_auth_bp.post("/logout")
def logout():
    logout_user()
    session.clear()

    return jsonify({
        "ok": True,
        "code": "LOGOUT_SUCCESS",
        "message": "Sesión cerrada correctamente",
    }), 200

@api_auth_bp.get("/me")
@login_required
def me():
    return jsonify({
        "ok": True,
        "code": "SESSION_ACTIVE",
        "data": {
            "usuario": {
                "id": current_user.id,
                "nombre": current_user.nombre,
                "correo": current_user.correo,
                "rol": current_user.rol,
            }
        },
    }), 200
