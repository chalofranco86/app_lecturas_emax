import os
from pathlib import Path
from uuid import uuid4

from werkzeug.utils import secure_filename


def ensure_upload_folder(upload_folder):
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder


def generate_unique_filename(uploaded_file, filename_prefix=None):
    original_filename = secure_filename(
        uploaded_file.filename or ""
    )

    extension = Path(original_filename).suffix.lower()

    if filename_prefix:
        identifier = secure_filename(filename_prefix)
    else:
        identifier = uuid4().hex

    if not identifier:
        identifier = uuid4().hex

    return f"{identifier}{extension}"


def save_uploaded_file(
    uploaded_file,
    upload_folder,
    current_path=None,
    filename_prefix=None,
):
    if uploaded_file is None or not uploaded_file.filename:
        return current_path

    ensure_upload_folder(upload_folder)

    filename = generate_unique_filename(
        uploaded_file,
        filename_prefix=filename_prefix,
    )

    save_path = os.path.join(upload_folder, filename)

    uploaded_file.save(save_path)

    # Evita guardar separadores exclusivos de Windows en MariaDB.
    return save_path.replace("\\", "/")
