from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from app.models.user import User
from app.repositories.user_repository import (
    get_user_by_name,
    insert_user,
)


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        contrasena = request.form.get('contrasena')

        usuario = get_user_by_name(nombre)

        if usuario and check_password_hash(
            usuario['contrasena'],
            contrasena,
        ):
            user = User(
                usuario['id'],
                usuario['nombre'],
                usuario['correo'],
                usuario['rol'],
            )

            login_user(user)
            return redirect(url_for('dashboard.root'))

        return render_template(
            'login.html',
            error='Nombre de usuario o contraseña incorrectos',
        )

    return render_template('login.html')


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
