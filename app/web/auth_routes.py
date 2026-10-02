from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from app.models.user import User
from app.repositories.user_repository import (
    get_user_by_name,
    insert_user,
)
from app.services.auth_service import (
    authenticate_user,
    cambiar_contrasena as cambiar_contrasena_service,
)


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        contrasena = request.form.get('contrasena')

        resultado = authenticate_user(nombre, contrasena)

        if not resultado["ok"]:
            return render_template(
                'login.html',
                error=resultado["message"],
            )

        user = resultado["user"]
        login_user(user)

        # 🔑 Primera vez: forzar cambio de contraseña
        if user.debe_cambiar_contrasena:
            return redirect(url_for('auth.cambiar_contrasena'))

        return redirect(url_for('dashboard.root'))

    return render_template('login.html')


@auth_bp.route('/cambiar-contrasena', methods=['GET', 'POST'])
@login_required
def cambiar_contrasena():
    # Si ya la cambió, mandarlo al panel
    if not current_user.debe_cambiar_contrasena:
        return redirect(url_for('dashboard.root'))

    if request.method == 'POST':
        contrasena_actual = request.form.get('contrasena_actual')
        nueva = request.form.get('nueva')
        confirmacion = request.form.get('confirmacion')

        # Verificar que la contraseña actual sea correcta
        usuario = get_user_by_name(current_user.nombre)

        if usuario is None:
            return render_template(
                'cambiar_contrasena.html',
                error='No se pudo recuperar la información del usuario',
            ), 500

        try:
            contrasena_valida = check_password_hash(
                usuario['contrasena'],
                contrasena_actual,
            )
        except (TypeError, ValueError):
            contrasena_valida = False

        if not contrasena_valida:
            return render_template(
                'cambiar_contrasena.html',
                error='La contraseña actual no es correcta',
            )

        resultado = cambiar_contrasena_service(
            current_user.id,
            contrasena_actual,
            nueva,
            confirmacion,
        )

        if not resultado["ok"]:
            return render_template(
                'cambiar_contrasena.html',
                errors=resultado.get("errors"),
            )

        # Actualizar la sesión para que no vuelva a exigir el cambio.
        user = User(
            current_user.id,
            current_user.nombre,
            current_user.correo,
            current_user.rol,
            debe_cambiar_contrasena=0,
        )
        login_user(user)

        flash('Contraseña actualizada correctamente', 'success')
        return redirect(url_for('dashboard.root'))

    return render_template('cambiar_contrasena.html')


@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        contrasena = request.form.get('contrasena')
        rol = request.form.get('rol')

        contrasena_cifrada = generate_password_hash(contrasena)

        resultado = insert_user(
            nombre,
            correo,
            contrasena_cifrada,
            rol,
        )

        if resultado is None:
            return render_template(
                'registro.html',
                error='No se pudo registrar el usuario',
            )

        return redirect(url_for('auth.login'))

    return render_template('registro.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


# 🔑 Blindaje: mientras la bandera esté activa, no dejar ir a ninguna otra ruta
@auth_bp.before_app_request
def forzar_cambio_contrasena():
    endpoint = request.endpoint

    if (
        current_user.is_authenticated
        and current_user.debe_cambiar_contrasena
        and endpoint not in ('auth.cambiar_contrasena', 'auth.logout')
    ):
        return redirect(url_for('auth.cambiar_contrasena'))