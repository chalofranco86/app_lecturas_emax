from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id, nombre, correo, rol):
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.rol = rol
