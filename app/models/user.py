# app/models/user.py
from flask_login import UserMixin

from app.extensions import login_manager
from app.infrastructure.database import execute_query


class User(UserMixin):
    def __init__(self, id, nombre, correo, rol, debe_cambiar_contrasena=0):
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.rol = rol
        self.debe_cambiar_contrasena = bool(debe_cambiar_contrasena)


@login_manager.user_loader
def load_user(user_id):
    query = """
    SELECT id, nombre, correo, rol, debe_cambiar_contrasena
    FROM usuarios
    WHERE id = %s
    """
    usuario = execute_query(query, (user_id,), fetch=True)

    if usuario:
        return User(
            usuario[0]["id"],
            usuario[0]["nombre"],
            usuario[0]["correo"],
            usuario[0]["rol"],
            usuario[0]["debe_cambiar_contrasena"],
        )

    return None