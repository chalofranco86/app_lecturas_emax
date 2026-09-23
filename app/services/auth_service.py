from werkzeug.security import check_password_hash

from app.models.user import User
from app.repositories.user_repository import get_user_by_name


def authenticate_user(nombre, contrasena):
    if not isinstance(nombre, str) or not nombre.strip():
        return {
            "ok": False,
            "code": "VALIDATION_ERROR",
            "message": "El nombre de usuario es obligatorio",
        }

    if not isinstance(contrasena, str) or not contrasena:
        return {
            "ok": False,
            "code": "VALIDATION_ERROR",
            "message": "La contraseña es obligatoria",
        }

    nombre = nombre.strip()
    usuario = get_user_by_name(nombre)

    if usuario is None:
        return {
            "ok": False,
            "code": "INVALID_CREDENTIALS",
            "message": "Usuario o contraseña incorrectos",
        }

    try:
        contrasena_correcta = check_password_hash(
            usuario["contrasena"],
            contrasena,
        )
    except (TypeError, ValueError):
        contrasena_correcta = False

    if not contrasena_correcta:
        return {
            "ok": False,
            "code": "INVALID_CREDENTIALS",
            "message": "Usuario o contraseña incorrectos",
        }

    user = User(
        usuario["id"],
        usuario["nombre"],
        usuario["correo"],
        usuario["rol"],
    )

    return {
        "ok": True,
        "code": "LOGIN_SUCCESS",
        "message": "Inicio de sesión correcto",
        "user": user,
        "data": {
            "usuario": {
                "id": usuario["id"],
                "nombre": usuario["nombre"],
                "correo": usuario["correo"],
                "rol": usuario["rol"],
            }
        },
    }
