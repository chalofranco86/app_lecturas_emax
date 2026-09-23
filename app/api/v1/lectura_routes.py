from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required

from app.services.lectura_service import create_lectura


api_lecturas_bp = Blueprint(
    "api_lecturas",
    __name__,
    url_prefix="/lecturas",
)


@api_lecturas_bp.post("")
@login_required
def registrar_lectura():
    resultado = create_lectura(
        data=request.form,
        foto_contador=request.files.get("foto_contador"),
        foto_inmueble=request.files.get("foto_inmueble"),
        usuario_id=current_user.id,
        upload_folder=current_app.config["UPLOAD_FOLDER"],
    )

    status_codes = {
        "LECTURA_CREATED": 201,
        "LECTURA_ALREADY_EXISTS": 200,
        "INVALID_CLIENT_UUID": 400,
        "CODIGO_INMUEBLE_REQUIRED": 400,
        "VALIDATION_ERROR": 400,
        "INMUEBLE_NOT_FOUND": 404,
        "FILE_STORAGE_ERROR": 500,
        "DATABASE_ERROR": 500,
    }

    status_code = status_codes.get(
        resultado["code"],
        500,
    )

    return jsonify(resultado), status_code
