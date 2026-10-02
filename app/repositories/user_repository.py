from werkzeug.security import generate_password_hash
from app.infrastructure.database import execute_query


def get_user_by_id(user_id):
    query = """
        SELECT id, nombre, correo, rol, debe_cambiar_contrasena
        FROM usuarios
        WHERE id = %s
    """
    usuarios = execute_query(query, (user_id,), fetch=True)

    if usuarios:
        return usuarios[0]

    return None
#Consulta para obtener un usuario por su nombre
def get_user_by_name(nombre):
    query = """
        SELECT id, nombre, correo, contrasena, rol, debe_cambiar_contrasena
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
        INSERT INTO usuarios (
            nombre,
            correo,
            contrasena,
            rol,
            debe_cambiar_contrasena
        )
        VALUES (%s, %s, %s, %s, 1)
    """
    params = (nombre, correo, contrasena_cifrada, rol)
    return execute_query(query, params)


def update_contrasena(user_id, nueva_contrasena_cifrada):
    """Actualiza la contraseña y apaga la bandera de cambio obligatorio."""
    query = """
    UPDATE usuarios
    SET contrasena = %s,
        debe_cambiar_contrasena = 0
    WHERE id = %s
    """
    return execute_query(query, (nueva_contrasena_cifrada, user_id))