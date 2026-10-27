from flask import (
    Blueprint,
    current_app,
    jsonify,
    request,
)
from flask_login import login_required

from app.repositories.inmueble_repository import (
    get_inmueble_by_codigo,
    get_inmueble_by_contador,
)

from app.repositories.lectura_repository import (
    get_lectura_anterior,
)

from app.services.sync_service import (
    prepare_route_download,
)

api_inmuebles_bp = Blueprint(
    "api_inmuebles",
    __name__,
    url_prefix="/inmuebles",
)

@api_inmuebles_bp.get(
    "/descarga-ruta"
)
@login_required
def descargar_ruta_offline():
    ruta = str(
        request.args.get("ruta") or ""
    ).strip()

    periodo_proceso = str(
        request.args.get(
            "periodo_proceso"
        ) or ""
    ).strip()

    sin_ruta_value = str(
        request.args.get(
            "sin_ruta"
        ) or ""
    ).strip().lower()

    valid_true_values = {
        "1",
        "true",
        "si",
        "sí",
    }

    valid_false_values = {
        "",
        "0",
        "false",
        "no",
    }

    if (
        sin_ruta_value
        not in (
            valid_true_values
            | valid_false_values
        )
    ):
        return jsonify({
            "ok": False,
            "code": "INVALID_SIN_RUTA",
            "message": (
                "sin_ruta debe ser 1, 0, "
                "true o false"
            ),
        }), 400

    sin_ruta = (
        sin_ruta_value
        in valid_true_values
    )

    try:
        result = prepare_route_download(
            periodo_value=periodo_proceso,
            ruta=ruta,
            sin_ruta=sin_ruta,
        )
    except Exception:
        current_app.logger.exception(
            "No fue posible preparar "
            "la descarga de ruta"
        )

        return jsonify({
            "ok": False,
            "code": "DATABASE_ERROR",
            "message": (
                "No fue posible obtener "
                "la información de la ruta"
            ),
        }), 500

    if not result["ok"]:
        return jsonify(result), 400

    return jsonify(result), 200

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
