import re

from datetime import date
from datetime import datetime
from datetime import timezone

from app.repositories.inmueble_repository import (
    get_inmuebles_for_offline_route,
)


PERIODO_PATTERN = re.compile(
    r"^\d{4}-(0[1-9]|1[0-2])$"
)


def parse_periodo_proceso(value):
    normalized_value = str(
        value or ""
    ).strip()

    if not PERIODO_PATTERN.fullmatch(
        normalized_value
    ):
        return None

    year, month = normalized_value.split(
        "-"
    )

    return date(
        int(year),
        int(month),
        1,
    )


def serialize_temporal_value(value):
    if isinstance(
        value,
        (datetime, date),
    ):
        return value.isoformat()

    return value


def build_lectura_anterior(row):
    if row.get("anterior_id") is None:
        return None

    return {
        "id":
            row.get("anterior_id"),

        "lectura":
            row.get("anterior_lectura"),

        "mes_proceso":
            row.get(
                "anterior_mes_proceso"
            ),

        "periodo_proceso":
            serialize_temporal_value(
                row.get(
                    "anterior_periodo_proceso"
                )
            ),

        "fecha_lectura":
            serialize_temporal_value(
                row.get(
                    "anterior_fecha_lectura"
                )
            ),
    }


def build_lectura_periodo(row):
    if row.get("periodo_id") is None:
        return None

    return {
        "id":
            row.get("periodo_id"),

        "client_uuid":
            row.get(
                "periodo_client_uuid"
            ),

        "lectura":
            row.get(
                "periodo_lectura"
            ),

        "mes_proceso":
            row.get(
                "periodo_mes_proceso"
            ),

        "periodo_proceso":
            serialize_temporal_value(
                row.get("periodo_fecha")
            ),

        "fecha_lectura":
            serialize_temporal_value(
                row.get(
                    "periodo_fecha_lectura"
                )
            ),
    }


def build_offline_inmueble(row):
    return {
        "id":
            row.get("id"),

        "codigo_tarjeta":
            row.get("codigo_tarjeta"),

        "nombre":
            row.get("nombre"),

        "direccion":
            row.get("direccion"),

        "tipo_inmueble":
            row.get("tipo_inmueble"),

        "nim":
            row.get("nim"),

        "ruta":
            row.get("ruta"),

        # El contador EMAX continúa utilizando
        # el campo heredado nit.
        "nit":
            row.get("nit"),

        "creado_en":
            serialize_temporal_value(
                row.get("creado_en")
            ),

        "correlativo":
            row.get("correlativo"),

        "contador_eemq":
            row.get("contador_eemq"),

        "lectura_anterior":
            build_lectura_anterior(
                row
            ),

        "lectura_periodo_actual":
            build_lectura_periodo(
                row
            ),
    }


def prepare_route_download(
    periodo_value,
    ruta=None,
    sin_ruta=False,
):
    periodo_proceso = (
        parse_periodo_proceso(
            periodo_value
        )
    )

    if periodo_proceso is None:
        return {
            "ok": False,
            "code": "INVALID_PERIOD",
            "message": (
                "periodo_proceso debe utilizar "
                "el formato YYYY-MM"
            ),
        }

    normalized_route = str(
        ruta or ""
    ).strip()

    if sin_ruta and normalized_route:
        return {
            "ok": False,
            "code": "ROUTE_FILTER_CONFLICT",
            "message": (
                "No puedes enviar ruta y sin_ruta "
                "al mismo tiempo"
            ),
        }

    if not sin_ruta and not normalized_route:
        return {
            "ok": False,
            "code": "ROUTE_REQUIRED",
            "message": (
                "Debes indicar una ruta o solicitar "
                "los inmuebles sin ruta"
            ),
        }

    rows = get_inmuebles_for_offline_route(
        periodo_proceso=periodo_proceso,
        ruta=(
            None
            if sin_ruta
            else normalized_route
        ),
        sin_ruta=sin_ruta,
    )

    inmuebles = [
        build_offline_inmueble(row)
        for row in rows
    ]

    return {
        "ok": True,
        "code": "ROUTE_DOWNLOAD_READY",
        "message": (
            "Información preparada "
            "para uso sin conexión"
        ),
        "data": {
            "ruta": (
                None
                if sin_ruta
                else normalized_route
            ),
            "sin_ruta": sin_ruta,
            "periodo_proceso":
                periodo_proceso.strftime(
                    "%Y-%m"
                ),
            "descargado_en":
                datetime.now(
                    timezone.utc
                ).isoformat(),
            "total": len(inmuebles),
            "inmuebles": inmuebles,
        },
    }