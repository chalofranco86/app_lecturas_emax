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

def get_inmuebles_for_offline_route(
    periodo_proceso,
    ruta=None,
    sin_ruta=False,
):
    if sin_ruta:
        route_condition = """
        i.ruta IS NULL
        """
        route_params = []
    else:
        route_condition = """
        TRIM(i.ruta) = %s
        """
        route_params = [ruta]

    query = f"""
    SELECT
        i.id,
        i.codigo_tarjeta,
        i.nombre,
        i.direccion,
        i.tipo_inmueble,
        i.nim,
        i.ruta,
        i.nit,
        i.creado_en,
        i.correlativo,
        i.contador_eemq,

        lectura_anterior.id
            AS anterior_id,
        lectura_anterior.lectura
            AS anterior_lectura,
        lectura_anterior.mes_proceso
            AS anterior_mes_proceso,
        lectura_anterior.periodo_proceso
            AS anterior_periodo_proceso,
        lectura_anterior.fecha_lectura
            AS anterior_fecha_lectura,

        lectura_periodo.id
            AS periodo_id,
        lectura_periodo.client_uuid
            AS periodo_client_uuid,
        lectura_periodo.lectura
            AS periodo_lectura,
        lectura_periodo.mes_proceso
            AS periodo_mes_proceso,
        lectura_periodo.periodo_proceso
            AS periodo_fecha,
        lectura_periodo.fecha_lectura
            AS periodo_fecha_lectura

    FROM inmuebles i

    LEFT JOIN lecturas lectura_anterior
        ON lectura_anterior.id = (
            SELECT la.id
            FROM lecturas la
            WHERE la.inmueble_id = i.id
              AND la.periodo_proceso < %s
            ORDER BY
                la.periodo_proceso DESC,
                la.fecha_lectura DESC,
                la.id DESC
            LIMIT 1
        )

    LEFT JOIN lecturas lectura_periodo
        ON lectura_periodo.id = (
            SELECT lp.id
            FROM lecturas lp
            WHERE lp.inmueble_id = i.id
              AND lp.periodo_proceso = %s
            ORDER BY
                lp.fecha_lectura DESC,
                lp.id DESC
            LIMIT 1
        )

    WHERE {route_condition}

    ORDER BY
        CASE
            WHEN NULLIF(
                TRIM(i.correlativo),
                ''
            ) IS NULL
            THEN 1
            ELSE 0
        END,
        i.correlativo,
        i.codigo_tarjeta
    """

    params = [
        periodo_proceso,
        periodo_proceso,
        *route_params,
    ]

    result = execute_query(
    query,
    tuple(params),
    fetch=True,
    )

    if result is None:
        raise RuntimeError(
            "No fue posible consultar "
            "los inmuebles de la ruta"
        )

    return result

#Funcion que debuelve un inmueble por su codigo de tarjeta o como un diccionario o NONE si no existe
def get_inmueble_by_codigo(codigo):
    query = "SELECT * FROM inmuebles WHERE codigo_tarjeta = %s"
    inmuebles = execute_query(query, (codigo,), fetch=True)

    if inmuebles:
        return inmuebles[0]

    return None


def get_inmueble_by_contador(contador):
    contador = str(contador or "").strip()

    if not contador:
        return None

    query = """
    SELECT *
    FROM inmuebles
    WHERE nit = %s
    LIMIT 1
    """

    inmuebles = execute_query(
        query,
        (contador,),
        fetch=True,
    )

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
