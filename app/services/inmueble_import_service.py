import csv
import io

from app.repositories.inmueble_repository import (
    get_inmueble_by_codigo,
    update_inmueble_fields,
)


IMPORTABLE_COLUMNS = {
    "correlativo": "correlativo",
    "contador_eemq": "contador_eemq",
}


def import_inmuebles_csv(file_storage):
    content = file_storage.read()

    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        return {
            "ok": False,
            "message": "El archivo debe estar codificado en UTF-8.",
        }

    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    headers = [header.strip() for header in (reader.fieldnames or [])]

    if "codigo_tarjeta" not in headers:
        return {
            "ok": False,
            "message": "El CSV debe incluir la columna codigo_tarjeta.",
        }

    importable_headers = [
        header for header in headers if header in IMPORTABLE_COLUMNS
    ]
    if not importable_headers:
        return {
            "ok": False,
            "message": "El CSV no incluye columnas actualizables.",
        }

    updated = 0
    not_found = []
    invalid_rows = []
    seen_codes = set()

    for row_number, row in enumerate(reader, start=2):
        row = {
            (key or "").strip(): value
            for key, value in row.items()
            if key is not None
        }
        codigo_tarjeta = (row.get("codigo_tarjeta") or "").strip()

        if not codigo_tarjeta or codigo_tarjeta in seen_codes:
            invalid_rows.append(row_number)
            continue

        seen_codes.add(codigo_tarjeta)
        inmueble = get_inmueble_by_codigo(codigo_tarjeta)

        if not inmueble:
            not_found.append(codigo_tarjeta)
            continue

        fields = {
            IMPORTABLE_COLUMNS[header]: (row.get(header) or "").strip()
            for header in importable_headers
        }
        update_inmueble_fields(codigo_tarjeta, fields)
        updated += 1

    return {
        "ok": True,
        "updated": updated,
        "not_found": not_found,
        "invalid_rows": invalid_rows,
    }