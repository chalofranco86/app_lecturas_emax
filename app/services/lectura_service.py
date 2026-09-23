from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from uuid import UUID

from app.infrastructure.file_storage import save_uploaded_file
from app.repositories.inmueble_repository import (
    get_inmueble_by_codigo,
)
from app.repositories.lectura_repository import (
    get_lectura_by_client_uuid,
    insert_lectura,
)


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

    mes_proceso = str(
        data.get("mes_proceso") or ""
    ).strip()

    if not mes_proceso:
        errores["mes_proceso"] = (
            "El mes de proceso es obligatorio"
        )
    elif len(mes_proceso) > 50:
        errores["mes_proceso"] = (
            "El mes de proceso no puede superar "
            "los 50 caracteres"
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

    try:
        fecha_captura = datetime.fromisoformat(
            fecha_captura_raw.replace("Z", "+00:00")
        )

        if fecha_captura.tzinfo is None:
            errores["fecha_captura"] = (
                "La fecha debe incluir su zona horaria"
            )
        else:
            # Guardar las nuevas capturas en UTC
            fecha_captura = (
                fecha_captura
                .astimezone(timezone.utc)
                .replace(tzinfo=None)
            )
    except (ValueError, TypeError):
        fecha_captura = None
        errores["fecha_captura"] = (
            "La fecha de captura debe tener formato ISO 8601"
        )

    observacion = str(
        data.get("observacion") or ""
    ).strip() or None

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

    # 5. Guardar fotografías
    try:
        path_contador = save_uploaded_file(
            foto_contador,
            upload_folder,
        )
        path_inmueble = save_uploaded_file(
            foto_inmueble,
            upload_folder,
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
