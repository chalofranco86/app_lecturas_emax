from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required


dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def root():
    if current_user.is_authenticated:
        return render_template(
            'panel.html',
            usuario=current_user,
        )

    return redirect(url_for('auth.login'))


@dashboard_bp.route('/index')
@login_required
def buscar_inmueble():
    return render_template('index.html')
