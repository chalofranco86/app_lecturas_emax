from app.infrastructure.database import execute_query

# Obtiene una lectura por ID, incluyendo información del inmueble y del usuario que realizó la lectura
def get_lectura_by_id(lectura_id):
    query = """
    SELECT
        l.id, i.codigo_tarjeta, i.nombre AS nombre_inmueble, i.direccion,
        u.nombre AS nombre_usuario, l.fecha_lectura, l.lectura, l.observacion,
        l.mes_proceso, l.foto_contador, l.foto_inmueble,
        l.coordenada_x, l.coordenada_y
    FROM lecturas l
    JOIN inmuebles i ON l.inmueble_id = i.id
    JOIN usuarios u ON l.usuario_id = u.id
    WHERE l.id = %s
    """
    lecturas = execute_query(query, (lectura_id,), fetch=True)

    if lecturas:
        return lecturas[0]

    return None

# Obtiene una lectura por client_uuid, incluyendo información del inmueble y del usuario que realizó la lectura
def get_lectura_by_client_uuid(client_uuid):
    query = """
    SELECT
        l.id,
        l.client_uuid,
        i.codigo_tarjeta,
        i.nombre AS nombre_inmueble,
        i.direccion,
        u.nombre AS nombre_usuario,
        l.fecha_lectura,
        l.lectura,
        l.observacion,
        l.mes_proceso,
        l.foto_contador,
        l.foto_inmueble,
        l.coordenada_x,
        l.coordenada_y
    FROM lecturas l
    JOIN inmuebles i
        ON l.inmueble_id = i.id
    JOIN usuarios u
        ON l.usuario_id = u.id
    WHERE l.client_uuid = %s
    LIMIT 1
    """

    lecturas = execute_query(
        query,
        (client_uuid,),
        fetch=True,
    )

    if lecturas:
        return lecturas[0]

    return None

def get_lecturas(codigo_inmueble=None):
    query = """
    SELECT
        l.id, i.codigo_tarjeta, i.nombre AS nombre_inmueble, i.direccion,
        u.nombre AS nombre_usuario, l.fecha_lectura, l.lectura, l.observacion,
        l.mes_proceso, l.foto_contador, l.foto_inmueble,
        l.coordenada_x, l.coordenada_y
    FROM lecturas l
    JOIN inmuebles i ON l.inmueble_id = i.id
    JOIN usuarios u ON l.usuario_id = u.id
    """

    params = ()

    if codigo_inmueble:
        query += " WHERE i.codigo_tarjeta LIKE %s"
        params = (f"%{codigo_inmueble}%",)

    query += " ORDER BY l.fecha_lectura DESC"

    return execute_query(query, params, fetch=True)
#Insers de lectura, incluyendo la inserción de las fotos y coordenadas
def insert_lectura(
    client_uuid,
    inmueble_id,
    usuario_id,
    path_contador,
    path_inmueble,
    fecha_lectura,
    lectura,
    observacion,
    mes_proceso,
    coordenada_x,
    coordenada_y,
):
    query = """
    INSERT INTO lecturas (
        client_uuid,
        inmueble_id,
        usuario_id,
        foto_contador,
        foto_inmueble,
        fecha_lectura,
        lectura,
        observacion,
        mes_proceso,
        coordenada_x,
        coordenada_y
    )
    VALUES (
        %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s
    )
    """

    params = (
        client_uuid,
        inmueble_id,
        usuario_id,
        path_contador,
        path_inmueble,
        fecha_lectura,
        lectura,
        observacion,
        mes_proceso,
        coordenada_x,
        coordenada_y,
    )

    resultado = execute_query(query, params)

    if resultado is None:
        return get_lectura_by_client_uuid(client_uuid)

    return get_lectura_by_client_uuid(client_uuid)
# Update de lectura, incluyendo la actualización de las fotos y coordenadas
def update_lectura(
    lectura_id,
    lectura,
    observacion,
    mes_proceso,
    coordenada_x,
    coordenada_y,
    path_contador,
    path_inmueble,
):
    query = """
    UPDATE lecturas
    SET
        lectura = %s,
        observacion = %s,
        mes_proceso = %s,
        coordenada_x = COALESCE(%s, coordenada_x),
        coordenada_y = COALESCE(%s, coordenada_y),
        foto_contador = %s,
        foto_inmueble = %s
    WHERE id = %s
    """

    params = (
        lectura,
        observacion,
        mes_proceso,
        coordenada_x,
        coordenada_y,
        path_contador,
        path_inmueble,
        lectura_id,
    )

    return execute_query(query, params)
# Delte de lectura por ID
def delete_lectura(lectura_id):
    query = "DELETE FROM lecturas WHERE id = %s"
    return execute_query(query, (lectura_id,))
