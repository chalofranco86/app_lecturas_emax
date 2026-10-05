# app/__init__.py
from flask import Flask

from app.config import Config
from app.extensions import login_manager
from app.infrastructure.file_storage import ensure_upload_folder
from app.models.user import User
from app.repositories.user_repository import get_user_by_id

from app.web.pwa_routes import pwa_bp

@login_manager.user_loader
def load_user(user_id):
    usuario = get_user_by_id(user_id)

    if usuario:
        return User(
            usuario["id"],
            usuario["nombre"],
            usuario["correo"],
            usuario["rol"],
            usuario.get("debe_cambiar_contrasena", 0),
        )

    return None


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.register_blueprint(pwa_bp)

    app.config["UPLOAD_FOLDER"] = ensure_upload_folder(
        app.config["UPLOAD_FOLDER"]
    )

    login_manager.init_app(app)

    register_blueprints(app)

    return app


def register_blueprints(app):
    from app.api.v1 import api_v1_bp
    from app.web.auth_routes import auth_bp
    from app.web.dashboard_routes import dashboard_bp
    from app.web.error_routes import errores_bp
    from app.web.inmueble_import_routes import inmueble_import_bp
    from app.web.lectura_routes import lecturas_bp
    #Interfaz Web
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(lecturas_bp)
    app.register_blueprint(errores_bp)
    app.register_blueprint(inmueble_import_bp)

    # API
    app.register_blueprint(api_v1_bp)