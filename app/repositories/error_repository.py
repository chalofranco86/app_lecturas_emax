from app.infrastructure.database import execute_query
# Obtiene un listado de errores, incluyendo información del usuario que registró el error
def get_errores(codigo_tarjeta=None):
    query = """
    SELECT
        ie.id,
        ie.client_uuid,
        ie.codigo_tarjeta,
        ie.direccion_servicio,
        ie.ruta,
        ie.tarifa,
        ie.contador_agua,
        ie.foto_contador,
        ie.foto_inmueble,
        ie.coordenada_x,
        ie.coordenada_y,
        ie.observaciones,
        ie.fecha_registro,
        u.nombre AS nombre_usuario
    FROM inmuebles_errores ie
    LEFT JOIN usuarios u ON ie.usuario_id = u.id
    """

    params = ()

    if codigo_tarjeta:
        query += " WHERE ie.codigo_tarjeta LIKE %s"
        params = (f"%{codigo_tarjeta}%",)

    query += " ORDER BY ie.fecha_registro DESC"

    return execute_query(query, params, fetch=True)
# Obtiene un error por ID, incluyendo información del usuario que registró el error
def get_error_by_id(error_id):
    query = """
    SELECT
        ie.id,
        ie.client_uuid,
        ie.codigo_tarjeta,
        ie.direccion_servicio,
        ie.ruta,
        ie.tarifa,
        ie.contador_agua,
        ie.foto_contador,
        ie.foto_inmueble,
        ie.coordenada_x,
        ie.coordenada_y,
        ie.observaciones,
        ie.fecha_registro,
        u.nombre AS nombre_usuario
    FROM inmuebles_errores ie
    LEFT JOIN usuarios u ON ie.usuario_id = u.id
    WHERE ie.id = %s
    """

    errores = execute_query(query, (error_id,), fetch=True)

    if errores:
        return errores[0]
    return None

def get_error_by_client_uuid(client_uuid):
    query = """
    SELECT
        ie.id,
        ie.client_uuid,
        ie.codigo_tarjeta,
        ie.direccion_servicio,
        ie.ruta,
        ie.tarifa,
        ie.contador_agua,
        ie.foto_contador,
        ie.foto_inmueble,
        ie.coordenada_x,
        ie.coordenada_y,
        ie.observaciones,
        ie.fecha_registro,
        ie.usuario_id,
        u.nombre AS nombre_usuario
    FROM inmuebles_errores ie
    LEFT JOIN usuarios u ON ie.usuario_id = u.id
    WHERE ie.client_uuid = %s
    """

    errores = execute_query(query, (client_uuid,), fetch=True)

    if errores:
        return errores[0]
    return None
# Consulta para crear un nuevo inmueble con error, incluyendo la información del usuario que lo registró


def insert_error(
    codigo_tarjeta,
    direccion_servicio,
    ruta,
    tarifa,
    contador_agua,
    path_contador,
    path_inmueble,
    coordenada_x,
    coordenada_y,
    observaciones,
    usuario_id,
    client_uuid=None,
    fecha_registro=None,
):
    query = """
    INSERT INTO inmuebles_errores (
        client_uuid,
        codigo_tarjeta,
        direccion_servicio,
        ruta,
        tarifa,
        contador_agua,
        foto_contador,
        foto_inmueble,
        coordenada_x,
        coordenada_y,
        observaciones,
        fecha_registro,
        usuario_id
    )
    VALUES (
        %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s,
        COALESCE(%s, CURRENT_TIMESTAMP),
        %s
    )
    """

    params = (
        client_uuid,
        codigo_tarjeta,
        direccion_servicio,
        ruta,
        tarifa,
        contador_agua,
        path_contador,
        path_inmueble,
        coordenada_x,
        coordenada_y,
        observaciones,
        fecha_registro,
        usuario_id,
    )

    return execute_query(query, params)
# Consulta para actualizar un inmueble con error, incluyendo la información del usuario que lo registró
def update_error(
    error_id,
    codigo_tarjeta,
    direccion_servicio,
    ruta,
    tarifa,
    contador_agua,
    path_contador,
    path_inmueble,
    coordenada_x,
    coordenada_y,
    observaciones,
):
    query = """
    UPDATE inmuebles_errores
    SET
        codigo_tarjeta = %s,
        direccion_servicio = %s,
        ruta = %s,
        tarifa = %s,
        contador_agua = %s,
        foto_contador = %s,
        foto_inmueble = %s,
        coordenada_x = %s,
        coordenada_y = %s,
        observaciones = %s
    WHERE id = %s
    """

    params = (
        codigo_tarjeta,
        direccion_servicio,
        ruta,
        tarifa,
        contador_agua,
        path_contador,
        path_inmueble,
        coordenada_x,
        coordenada_y,
        observaciones,
        error_id,
    )

    return execute_query(query, params)
# Consulta para eliminar un inmueble con error por ID
def delete_error(error_id):
    query = "DELETE FROM inmuebles_errores WHERE id = %s"
    return execute_query(query, (error_id,))
