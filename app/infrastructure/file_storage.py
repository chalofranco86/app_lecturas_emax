import os

from werkzeug.utils import secure_filename

# Función para asegurar que la carpeta de subida exista
def ensure_upload_folder(upload_folder):
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder

# Función para guardar un archivo subido en una carpeta específica
def save_uploaded_file(uploaded_file, upload_folder):
    if not uploaded_file or not uploaded_file.filename:
        return None

    filename = secure_filename(uploaded_file.filename)
    file_path = os.path.join(upload_folder, filename)

    uploaded_file.save(file_path)

    return file_path
#
