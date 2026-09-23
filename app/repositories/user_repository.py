from app.infrastructure.database import execute_query


def get_user_by_id(user_id):
    query = "SELECT id, nombre, correo, rol FROM usuarios WHERE id = %s"
    usuarios = execute_query(query, (user_id,), fetch=True)

    if usuarios:
        return usuarios[0]

    return None
#Consulta para obtener un usuario por su nombre
def get_user_by_name(nombre):
    query = """
        SELECT id, nombre, correo, contrasena, rol
        FROM usuarios
        WHERE nombre = %s
    """
    usuarios = execute_query(query, (nombre,), fetch=True)

    if usuarios:
        return usuarios[0]

    return None
#Consulta para crear un nuevo usuario
def insert_user(nombre, correo, contrasena_cifrada, rol):
    query = """
        INSERT INTO usuarios (nombre, correo, contrasena, rol)
        VALUES (%s, %s, %s, %s)
    """
    params = (nombre, correo, contrasena_cifrada, rol)
    return execute_query(query, params)
