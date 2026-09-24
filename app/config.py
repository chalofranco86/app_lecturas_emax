# app/config.py
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    #"port": 3307,
    "database": "lectores_agua",
    "collation": "utf8mb4_general_ci",  # Collation compatible con versiones antiguas
    "charset": "utf8mb4"  # Charset compatible
}


class Config:
    SECRET_KEY = 'tu_clave_secreta_aqui_cambiala_por_una_segura'
    UPLOAD_FOLDER = 'app/static/uploads'
