from flask import (
    Blueprint,
    current_app,
    render_template,
    send_from_directory,
)

pwa_bp = Blueprint("pwa", __name__)

@pwa_bp.get("/offline")
def offline():
    return render_template("offline.html")


@pwa_bp.get("/service-worker.js")
def service_worker():
    response = send_from_directory(
        current_app.static_folder,
        "service-worker.js",
    )

    response.headers["Content-Type"] = (
        "application/javascript; charset=utf-8"
    )
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Service-Worker-Allowed"] = "/"

    return response

@pwa_bp.get("/captura")
def captura():
    return render_template("captura.html")
