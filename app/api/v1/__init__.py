from flask import Blueprint

from app.api.v1.auth_routes import api_auth_bp
from app.api.v1.error_routes import api_errores_bp
from app.api.v1.health_routes import api_health_bp
from app.api.v1.inmueble_routes import api_inmuebles_bp
from app.api.v1.lectura_routes import api_lecturas_bp
from app.api.v1.sync_routes import api_sync_bp


api_v1_bp = Blueprint(
    "api_v1",
    __name__,
    url_prefix="/api/v1",
)

api_v1_bp.register_blueprint(api_health_bp)
api_v1_bp.register_blueprint(api_auth_bp)
api_v1_bp.register_blueprint(api_inmuebles_bp)
api_v1_bp.register_blueprint(api_lecturas_bp)
api_v1_bp.register_blueprint(api_errores_bp)
api_v1_bp.register_blueprint(api_sync_bp)
