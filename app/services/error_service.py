from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from uuid import UUID

from app.infrastructure.file_storage import save_uploaded_file
from app.repositories.error_repository import (
    get_error_by_client_uuid,
    insert_error,
)


def create_error(
    data,
    foto_contador,
    foto_inmueble,
    usuario_id,
    upload_folder,
):
    data = data or {}

    # 1. Validar client_uuid
    client_uuid = str(data.get("client_uuid") or "").strip()

    if not client_uuid:
        return {
            "ok": False,
            "code": "CLIENT_UUID_REQUIRED",
            "message": "client_uuid es obligatorio",
        }

    try:
        client_uuid = str(UUID(client_uuid))
    except (ValueError, TypeError, AttributeError):
        return {
            "ok": False,
            "code": "INVALID_CLIENT_UUID",
            "message": "client_uuid no contiene un UUID válido",
        }

    # 2. Comprobar idempotencia antes de validar archivos
    error_existente = get_error_by_client_uuid(client_uuid)

    if error_existente:
        return {
            "ok": True,
            "created": False,
            "code": "INMUEBLE_ERROR_ALREADY_EXISTS",
            "message": "El error ya había sido sincronizado",
            "data": error_existente,
        }

    # 3. Validar usuario autenticado
    if not usuario_id:
        return {
            "ok": False,
            "code": "UNAUTHORIZED",
            "message": "No se encontró un usuario autenticado",
        }

    # 4. Validar código de tarjeta
    codigo_tarjeta = str(data.get("codigo_tarjeta") or "").strip()

    if not codigo_tarjeta:
        return {
            "ok": False,
            "code": "CODIGO_TARJETA_REQUIRED",
            "message": "El código de tarjeta es obligatorio",
        }

    if len(codigo_tarjeta) > 50:
        return {
            "ok": False,
            "code": "VALIDATION_ERROR",
            "message": "El código de tarjeta no puede superar 50 caracteres",
        }

    # 5. Campos de texto opcionales
    direccion_servicio = str(
        data.get("direccion_servicio") or ""
    ).strip() or None

    ruta = str(data.get("ruta") or "").strip() or None

    contador_agua = str(
        data.get("contador_agua") or ""
    ).strip() or None

    if direccion_servicio and len(direccion_servicio) > 255:
        return {
            "ok": False,
            "code": "VALIDATION_ERROR",
            "message": "La dirección no puede superar 255 caracteres",
        }

    if ruta and len(ruta) > 100:
        return {
            "ok": False,
            "code": "VALIDATION_ERROR",
            "message": "La ruta no puede superar 100 caracteres",
        }

    if contador_agua and len(contador_agua) > 50:
        return {
            "ok": False,
            "code": "VALIDATION_ERROR",
            "message": "El contador de agua no puede superar 50 caracteres",
        }

    # 6. Validar observaciones
    observaciones = str(data.get("observaciones") or "").strip()

    if not observaciones:
        return {
            "ok": False,
            "code": "OBSERVACIONES_REQUIRED",
            "message": "Las observaciones son obligatorias",
        }

    # 7. Validar tarifa opcional
    tarifa_texto = str(data.get("tarifa") or "").strip()
    tarifa = None

    if tarifa_texto:
        try:
            tarifa = Decimal(tarifa_texto)

            if not tarifa.is_finite():
                raise InvalidOperation

            if tarifa < 0:
                return {
                    "ok": False,
                    "code": "VALIDATION_ERROR",
                    "message": "La tarifa no puede ser negativa",
                }

        except (InvalidOperation, ValueError):
            return {
                "ok": False,
                "code": "VALIDATION_ERROR",
                "message": "La tarifa debe contener un número decimal válido",
            }

    # 8. Validar coordenadas obligatorias
    coordenada_x_texto = str(
        data.get("coordenada_x") or ""
    ).strip()

    coordenada_y_texto = str(
        data.get("coordenada_y") or ""
    ).strip()

    if not coordenada_x_texto or not coordenada_y_texto:
        return {
            "ok": False,
            "code": "COORDINATES_REQUIRED",
            "message": "Las coordenadas son obligatorias",
        }

    try:
        coordenada_x = Decimal(coordenada_x_texto)
        coordenada_y = Decimal(coordenada_y_texto)

        if not coordenada_x.is_finite() or not coordenada_y.is_finite():
            raise InvalidOperation

    except (InvalidOperation, ValueError):
        return {
            "ok": False,
            "code": "INVALID_COORDINATES",
            "message": "Las coordenadas deben contener números válidos",
        }

    if coordenada_x < Decimal("-180") or coordenada_x > Decimal("180"):
        return {
            "ok": False,
            "code": "INVALID_COORDINATES",
            "message": "La longitud debe estar entre -180 y 180",
        }

    if coordenada_y < Decimal("-90") or coordenada_y > Decimal("90"):
        return {
            "ok": False,
            "code": "INVALID_COORDINATES",
            "message": "La latitud debe estar entre -90 y 90",
        }

    # 9. Validar fecha generada por la PWA
    fecha_captura = str(data.get("fecha_captura") or "").strip()

    if not fecha_captura:
        return {
            "ok": False,
            "code": "FECHA_CAPTURA_REQUIRED",
            "message": "La fecha de captura es obligatoria",
        }

    try:
        fecha_iso = fecha_captura

        if fecha_iso.endswith("Z"):
            fecha_iso = fecha_iso[:-1] + "+00:00"

        fecha_registro = datetime.fromisoformat(fecha_iso)

        if fecha_registro.tzinfo is None:
            return {
                "ok": False,
                "code": "INVALID_CAPTURE_DATE",
                "message": (
                    "La fecha de captura debe incluir la zona horaria"
                ),
            }

        fecha_registro = (
            fecha_registro
            .astimezone(timezone.utc)
            .replace(tzinfo=None)
        )

    except ValueError:
        return {
            "ok": False,
            "code": "INVALID_CAPTURE_DATE",
            "message": "La fecha de captura no tiene un formato ISO válido",
        }

    # 10. Guardar fotografías opcionales
    path_contador = None
    path_inmueble = None

    try:
        if foto_contador and foto_contador.filename:
            path_contador = save_uploaded_file(
                foto_contador,
                upload_folder,
            )

        if foto_inmueble and foto_inmueble.filename:
            path_inmueble = save_uploaded_file(
                foto_inmueble,
                upload_folder,
            )

    except (OSError, ValueError) as error:
        return {
            "ok": False,
            "code": "FILE_STORAGE_ERROR",
            "message": f"No fue posible guardar las fotografías: {error}",
        }

    # 11. Insertar el registro
    insertado = insert_error(
        codigo_tarjeta=codigo_tarjeta,
        direccion_servicio=direccion_servicio,
        ruta=ruta,
        tarifa=tarifa,
        contador_agua=contador_agua,
        path_contador=path_contador,
        path_inmueble=path_inmueble,
        coordenada_x=coordenada_x,
        coordenada_y=coordenada_y,
        observaciones=observaciones,
        usuario_id=usuario_id,
        client_uuid=client_uuid,
        fecha_registro=fecha_registro,
    )

    # 12. Recuperar el registro por su UUID
    error_registrado = get_error_by_client_uuid(client_uuid)

    if error_registrado:
        # Si el INSERT falló por una petición concurrente, el índice UNIQUE
        # garantiza que recuperemos el registro creado por la otra petición.
        if not insertado:
            return {
                "ok": True,
                "created": False,
                "code": "INMUEBLE_ERROR_ALREADY_EXISTS",
                "message": "El error ya había sido sincronizado",
                "data": error_registrado,
            }

        return {
            "ok": True,
            "created": True,
            "code": "INMUEBLE_ERROR_CREATED",
            "message": "Inmueble con error registrado correctamente",
            "data": error_registrado,
        }

    return {
        "ok": False,
        "code": "DATABASE_ERROR",
        "message": "No fue posible registrar el inmueble con error",
    }
