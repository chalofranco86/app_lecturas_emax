import re

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from uuid import UUID

from app.infrastructure.file_storage import save_uploaded_file
from app.repositories.inmueble_repository import (
    get_inmueble_by_codigo,
)
from app.repositories.lectura_repository import (
    get_lectura_by_client_uuid,
    get_lectura_by_inmueble_and_periodo,
    insert_lectura,
)


MESES_ES = (
    "ENERO",
    "FEBRERO",
    "MARZO",
    "ABRIL",
    "MAYO",
    "JUNIO",
    "JULIO",
    "AGOSTO",
    "SEPTIEMBRE",
    "OCTUBRE",
    "NOVIEMBRE",
    "DICIEMBRE",
)

PERIODO_PROCESO_PATTERN = re.compile(
    r"^(?P<anio>\d{4})-(?P<mes>0[1-9]|1[0-2])$"
)

def normalizar_periodo_proceso(valor):
    """
    Recibe YYYY-MM y genera:

        periodo_proceso: date, por ejemplo 2026-09-01
        mes_proceso: str, por ejemplo SEPTIEMBRE 2026
    """
    valor = str(valor or "").strip()

    coincidencia = PERIODO_PROCESO_PATTERN.fullmatch(
        valor
    )

    if coincidencia is None:
        return None, None

    anio = int(coincidencia.group("anio"))
    mes = int(coincidencia.group("mes"))

    if not 1900 <= anio <= 2100:
        return None, None

    periodo_proceso = datetime(
        anio,
        mes,
        1,
    ).date()

    mes_proceso = (
        f"{MESES_ES[mes - 1]} {anio}"
    )

    return periodo_proceso, mes_proceso

def create_lectura(
    data,
    foto_contador,
    foto_inmueble,
    usuario_id,
    upload_folder,
):
    # 1. Validar y normalizar UUID
    client_uuid = str(
        data.get("client_uuid") or ""
    ).strip()

    try:
        client_uuid = str(UUID(client_uuid))
    except (ValueError, TypeError, AttributeError):
        return {
            "ok": False,
            "code": "INVALID_CLIENT_UUID",
            "message": "client_uuid no contiene un UUID válido",
        }

    # 2. Idempotencia: revisar antes de validar archivos
    lectura_existente = get_lectura_by_client_uuid(
        client_uuid
    )

    if lectura_existente:
        return {
            "ok": True,
            "code": "LECTURA_ALREADY_EXISTS",
            "message": "La lectura ya había sido sincronizada",
            "created": False,
            "data": lectura_existente,
        }

    # 3. Validar código y buscar inmueble
    codigo_inmueble = str(
        data.get("codigo_inmueble") or ""
    ).strip()

    if not codigo_inmueble:
        return {
            "ok": False,
            "code": "CODIGO_INMUEBLE_REQUIRED",
            "message": "El código del inmueble es obligatorio",
        }

    inmueble = get_inmueble_by_codigo(codigo_inmueble)

    if inmueble is None:
        return {
            "ok": False,
            "code": "INMUEBLE_NOT_FOUND",
            "message": (
                "No se encontró el inmueble con código "
                f"{codigo_inmueble}"
            ),
            "next_action": "REGISTER_ERROR",
        }

    # 4. Validar los demás campos
    errores = {}

    lectura_raw = str(
        data.get("lectura") or ""
    ).strip()

    try:
        lectura = int(lectura_raw)

        if lectura < 0:
            errores["lectura"] = (
                "La lectura no puede ser negativa"
            )
    except (ValueError, TypeError):
        lectura = None
        errores["lectura"] = (
            "La lectura es obligatoria y debe ser un entero"
        )

    coordenada_x_raw = data.get("coordenada_x")
    coordenada_y_raw = data.get("coordenada_y")

    try:
        coordenada_x = Decimal(
            str(coordenada_x_raw).strip()
        )

        if not coordenada_x.is_finite():
            raise InvalidOperation

        if not Decimal("-180") <= coordenada_x <= Decimal("180"):
            errores["coordenada_x"] = (
                "La longitud debe estar entre -180 y 180"
            )
    except (InvalidOperation, ValueError, TypeError):
        coordenada_x = None
        errores["coordenada_x"] = (
            "La longitud es obligatoria y debe ser decimal"
        )

    try:
        coordenada_y = Decimal(
            str(coordenada_y_raw).strip()
        )

        if not coordenada_y.is_finite():
            raise InvalidOperation

        if not Decimal("-90") <= coordenada_y <= Decimal("90"):
            errores["coordenada_y"] = (
                "La latitud debe estar entre -90 y 90"
            )
    except (InvalidOperation, ValueError, TypeError):
        coordenada_y = None
        errores["coordenada_y"] = (
            "La latitud es obligatoria y debe ser decimal"
        )

    fecha_captura_raw = str(
        data.get("fecha_captura") or ""
    ).strip()

    fecha_captura = None
    periodo_proceso = None
    mes_proceso = None

    try:
        fecha_captura_con_zona = datetime.fromisoformat(
            echa_captura_raw = str(
        data.get("fecha_captura") or ""
    ).strip()
        )

        if fecha_captura_con_zona.tzinfo is None:
            errores["fecha_captura"] = (
                "La fecha debe incluir su zona horaria"
            )
        else:
            (
                periodo_proceso,
                mes_proceso,
            ) = calcular_periodo_proceso(
                fecha_captura_con_zona
            )

            # MariaDB almacenará la captura en UTC.
            fecha_captura = (
                fecha_captura_con_zona
                .astimezone(timezone.utc)
                .replace(tzinfo=None)
            )

    except (ValueError, TypeError):
        errores["fecha_captura"] = (
            "La fecha de captura debe tener "
            "formato ISO 8601"
        )

    if errores:
        return {
            "ok": False,
            "code": "VALIDATION_ERROR",
            "message": "Existen datos inválidos",
            "errors": errores,
        }

    observacion = str(
        data.get("observacion") or ""
    ).strip() or None

    # 🔑 Observación Tipo (cambio de contador)
    contador_cambiado = str(
        data.get("contador_cambiado") or ""
    ).strip().lower()

    observacion_tipo = str(
        data.get("observacion_tipo") or ""
    ).strip() or None

    if contador_cambiado == "si":
        if not observacion_tipo:
            errores["observacion_tipo"] = (
                "Debes describir el cambio del contador "
                "en Observación Tipo"
            )
        elif len(observacion_tipo) > 255:
            errores["observacion_tipo"] = (
                "La observación tipo no puede superar "
                "los 255 caracteres"
            )
    else:
        # Si no hubo cambio, no guardar nada
        observacion_tipo = None

    if usuario_id is None:
        errores["usuario_id"] = (
            "No se pudo identificar al usuario"
        )

    if (
        foto_contador is None
        or not getattr(foto_contador, "filename", "")
    ):
        errores["foto_contador"] = (
            "La fotografía del contador es obligatoria"
        )

    if (
        foto_inmueble is None
        or not getattr(foto_inmueble, "filename", "")
    ):
        errores["foto_inmueble"] = (
            "La fotografía del inmueble es obligatoria"
        )

    if errores:
        return {
            "ok": False,
            "code": "VALIDATION_ERROR",
            "message": "Existen datos inválidos",
            "errors": errores,
        }

    # 5. Impedir más de una lectura por inmueble
    # y periodo de proceso.
    lectura_del_periodo = (
        get_lectura_by_inmueble_and_periodo(
            inmueble_id=inmueble["id"],
            periodo_proceso=periodo_proceso,
        )
    )

    if lectura_del_periodo:
        return {
            "ok": False,
            "created": False,
            "code": "LECTURA_PERIOD_ALREADY_EXISTS",
            "message": (
                "El inmueble ya tiene una lectura "
                f"registrada para {mes_proceso}"
            ),
            "data": lectura_del_periodo,
        }

    # 5. Guardar fotografías
    try:
        path_contador = save_uploaded_file(
            foto_contador,
            upload_folder,
            filename_prefix=f"lectura_{client_uuid}_contador",
        )
        path_inmueble = save_uploaded_file(
            foto_inmueble,
            upload_folder,
            filename_prefix=f"lectura_{client_uuid}_inmueble",
        )
    except OSError:
        return {
            "ok": False,
            "code": "FILE_STORAGE_ERROR",
            "message": (
                "No fue posible guardar las fotografías"
            ),
        }

    if not path_contador or not path_inmueble:
        return {
            "ok": False,
            "code": "FILE_STORAGE_ERROR",
            "message": (
                "No fue posible guardar las fotografías"
            ),
        }

    # 6. Insertar la lectura
    lectura_creada = insert_lectura(
        client_uuid=client_uuid,
        inmueble_id=inmueble["id"],
        usuario_id=usuario_id,
        path_contador=path_contador,
        path_inmueble=path_inmueble,
        fecha_lectura=fecha_captura,
        lectura=lectura,
        observacion=observacion,
        observacion_tipo=observacion_tipo,   # ← nuevo
        mes_proceso=mes_proceso,
        coordenada_x=coordenada_x,
        coordenada_y=coordenada_y,
    )

    if lectura_creada is None:
        return {
            "ok": False,
            "code": "DATABASE_ERROR",
            "message": (
                "No fue posible registrar la lectura"
            ),
        }

    return {
        "ok": True,
        "code": "LECTURA_CREATED",
        "message": "Lectura registrada correctamente",
        "created": True,
        "data": lectura_creada,
    }
