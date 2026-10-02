from app.infrastructure.database import execute_query

def update_inmueble_fields(codigo_tarjeta, fields):
    allowed_fields = {
        "correlativo",
        "contador_eemq",
    }
    updates = {
        field: value
        for field, value in fields.items()
        if field in allowed_fields
    }

    if not updates:
        return False

    assignments = ", ".join(f"{field} = %s" for field in updates)
    params = tuple(updates.values()) + (codigo_tarjeta,)
    query = f"UPDATE inmuebles SET {assignments} WHERE codigo_tarjeta = %s"
    return execute_query(query, params)

def get_rutas():
    query = """
    SELECT DISTINCT ruta
    FROM inmuebles
    WHERE ruta IS NOT NULL AND ruta <> ''
    ORDER BY ruta
    """
    return execute_query(query, fetch=True) or []

#Funcion que debuelve un inmueble por su codigo de tarjeta o como un diccionario o NONE si no existe
def get_inmueble_by_codigo(codigo):
    query = "SELECT * FROM inmuebles WHERE codigo_tarjeta = %s"
    inmuebles = execute_query(query, (codigo,), fetch=True)

    if inmuebles:
        return inmuebles[0]

    return None


def get_inmueble_by_contador(contador):
    query = "SELECT * FROM inmuebles WHERE nit = %s"
    inmuebles = execute_query(query, (contador,), fetch=True)

    if inmuebles:
        return inmuebles[0]

    return None


#Buscar un inmueble por su codigo de tarjeta
def get_inmueble_id_by_codigo(codigo):
    query = "SELECT id FROM inmuebles WHERE codigo_tarjeta = %s"
    inmuebles = execute_query(query, (codigo,), fetch=True)

    if inmuebles:
        return inmuebles[0]["id"]

    return None
