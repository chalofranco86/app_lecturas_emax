from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required

from app.services.error_service import create_error


api_errores_bp = Blueprint(
    "api_errores",
    __name__,
)


@api_errores_bp.route("/errores", methods=["POST"])
@login_required
def registrar_error():
    # Permite multipart/form-data y JSON cuando no existen fotografías.
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form.to_dict()

    foto_contador = request.files.get("foto_contador")
    foto_inmueble = request.files.get("foto_inmueble")

    resultado = create_error(
        data=data,
        foto_contador=foto_contador,
        foto_inmueble=foto_inmueble,
        usuario_id=current_user.id,
        upload_folder=current_app.config["UPLOAD_FOLDER"],
    )

    if resultado.get("ok"):
        status_code = 201 if resultado.get("created") else 200
        return jsonify(resultado), status_code

    validation_codes = {
        "CLIENT_UUID_REQUIRED",
        "INVALID_CLIENT_UUID",
        "CODIGO_TARJETA_REQUIRED",
        "OBSERVACIONES_REQUIRED",
        "COORDINATES_REQUIRED",
        "INVALID_COORDINATES",
        "FECHA_CAPTURA_REQUIRED",
        "INVALID_CAPTURE_DATE",
        "VALIDATION_ERROR",
    }

    if resultado.get("code") in validation_codes:
        return jsonify(resultado), 400

    if resultado.get("code") == "UNAUTHORIZED":
        return jsonify(resultado), 401

    if resultado.get("code") in {
        "FILE_STORAGE_ERROR",
        "DATABASE_ERROR",
    }:
        return jsonify(resultado), 500

    return jsonify(resultado), 500
