# app/routes/upload.py
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from app.models.database import execute_query

upload_bp = Blueprint('upload', __name__)

# Configurar carpeta para guardar imágenes
UPLOAD_FOLDER = 'app/static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@upload_bp.route('/upload', methods=['POST'])
def upload_images():
    if 'foto_contador' not in request.files or 'foto_inmueble' not in request.files:
        return jsonify({"error": "Faltan imágenes"}), 400

    foto_contador = request.files['foto_contador']
    foto_inmueble = request.files['foto_inmueble']
    inmueble_id = request.form.get('inmueble_id')
    usuario_id = request.form.get('usuario_id')

    if not inmueble_id or not usuario_id:
        return jsonify({"error": "Faltan datos"}), 400

    # Guardar imágenes
    filename_contador = secure_filename(foto_contador.filename)
    filename_inmueble = secure_filename(foto_inmueble.filename)
    path_contador = os.path.join(UPLOAD_FOLDER, filename_contador)
    path_inmueble = os.path.join(UPLOAD_FOLDER, filename_inmueble)

    foto_contador.save(path_contador)
    foto_inmueble.save(path_inmueble)

    # Guardar en la base de datos
    query = """
    INSERT INTO lecturas (inmueble_id, usuario_id, foto_contador, foto_inmueble)
    VALUES (%s, %s, %s, %s)
    """
    params = (inmueble_id, usuario_id, path_contador, path_inmueble)
    execute_query(query, params)

    return jsonify({"message": "Imágenes subidas correctamente"}), 201