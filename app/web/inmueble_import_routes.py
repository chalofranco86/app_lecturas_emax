from flask import Blueprint, render_template, request
from flask_login import login_required

from app.services.inmueble_import_service import import_inmuebles_csv


inmueble_import_bp = Blueprint("inmueble_import", __name__)


@inmueble_import_bp.route("/inmuebles/importar", methods=["GET", "POST"])
@login_required
def importar_inmuebles():
    result = None

    if request.method == "POST":
        file = request.files.get("archivo_csv")

        if not file or not file.filename:
            result = {
                "ok": False,
                "message": "Selecciona un archivo CSV.",
            }
        else:
            result = import_inmuebles_csv(file)

    return render_template("importar_inmuebles.html", result=result)