from flask import Blueprint, jsonify
from flask_login import login_required

from app.repositories.inmueble_repository import (
    get_inmueble_by_codigo,
    get_inmueble_by_contador,
)

from app.repositories.lectura_repository import (
    get_lectura_anterior,
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

    inmueble_data = dict(inmueble)

    inmueble_data["lectura_anterior"] = (
        get_lectura_anterior(
            inmueble["id"]
        )
    )

    return jsonify({
        "data": inmueble_data,
    }), 200


@api_inmuebles_bp.get(
    "/por-contador/<contador>"
)
@login_required
def obtener_inmueble_por_contador(contador):
    contador = str(contador or "").strip()

    if not contador:
        return jsonify({
            "error": {
                "code": "CONTADOR_REQUIRED",
                "message": (
                    "El número de contador es obligatorio"
                ),
            }
        }), 400

    inmueble = get_inmueble_by_contador(
        contador
    )

    if inmueble is None:
        return jsonify({
            "error": {
                "code": "INMUEBLE_NOT_FOUND",
                "message": (
                    "No se encontró un inmueble con "
                    f"el contador {contador}"
                ),
            }
        }), 404

    lectura_anterior = get_lectura_anterior(
        inmueble["id"]
    )

    inmueble["lectura_anterior"] = (
        lectura_anterior
    )

    return jsonify({
        "data": inmueble,
    }), 200
