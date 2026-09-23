from flask import Blueprint, jsonify
from flask_login import login_required

from app.repositories.inmueble_repository import (
    get_inmueble_by_codigo,
)


api_inmuebles_bp = Blueprint(
    "api_inmuebles",
    __name__,
    url_prefix="/inmuebles",
)


@api_inmuebles_bp.get("/<codigo>")
@login_required
def obtener_inmueble(codigo):
    codigo_normalizado = codigo.strip()

    if not codigo_normalizado:
        return jsonify({
            "error": {
                "code": "INVALID_CODIGO",
                "message": "El código del inmueble es obligatorio",
            }
        }), 400

    inmueble = get_inmueble_by_codigo(codigo_normalizado)

    if inmueble is None:
        return jsonify({
            "error": {
                "code": "INMUEBLE_NOT_FOUND",
                "message": (
                    "No se encontró un inmueble con el código "
                    f"{codigo_normalizado}"
                ),
            }
        }), 404

    return jsonify({
        "data": inmueble,
    }), 200
