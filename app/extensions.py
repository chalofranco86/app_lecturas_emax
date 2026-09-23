from flask import jsonify, redirect, request, url_for
from flask_login import LoginManager


login_manager = LoginManager()
login_manager.login_view = "auth.login"


@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith("/api/"):
        return jsonify({
            "error": {
                "code": "UNAUTHORIZED",
                "message": "Se requiere autenticación",
            }
        }), 401

    return redirect(
        url_for(
            login_manager.login_view,
            next=request.url,
        )
    )
