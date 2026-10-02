from werkzeug.security import check_password_hash, generate_password_hash

from app.models.user import User
from app.repositories.user_repository import get_user_by_name, update_contrasena


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

    # 🔑 Pasar la bandera al modelo User
    user = User(
        usuario["id"],
        usuario["nombre"],
        usuario["correo"],
        usuario["rol"],
        debe_cambiar_contrasena=usuario.get("debe_cambiar_contrasena", 0),
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
                "debe_cambiar_contrasena": usuario.get(
                    "debe_cambiar_contrasena", 0
                ),
            }
        },
    }


# 🔑 Nueva función: cambio de contraseña del primer login
def cambiar_contrasena(user_id, actual, nueva, confirmacion):
    """Valida y cambia la contraseña. Apaga la bandera al actualizar."""
    errores = {}

    if not nueva or not confirmacion:
        errores["nueva"] = "La nueva contraseña y su confirmación son obligatorias"
    elif nueva != confirmacion:
        errores["confirmacion"] = "Las contraseñas no coinciden"
    elif len(nueva) < 8:
        errores["nueva"] = "La nueva contraseña debe tener al menos 8 caracteres"

    if errores:
        return {"ok": False, "code": "VALIDATION_ERROR", "errors": errores}

    contrasena_cifrada = generate_password_hash(nueva)

    resultado = update_contrasena(user_id, contrasena_cifrada)

    if resultado is None:
        return {
            "ok": False,
            "code": "DATABASE_ERROR",
            "errors": {"general": "No fue posible actualizar la contraseña"},
        }

    return {"ok": True, "code": "PASSWORD_UPDATED"}