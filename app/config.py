import os


def environment_flag(name, default="0"):
    return os.getenv(
        name,
        default,
    ).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


DB_CONFIG = {
    "host": os.getenv(
        "DB_HOST",
        "localhost",
    ),
    "user": os.getenv(
        "DB_USER",
        "root",
    ),
    "password": os.getenv(
        "DB_PASSWORD",
        "",
    ),
    "port": int(
        os.getenv(
            "DB_PORT",
            "3306",
        )
    ),
    "database": os.getenv(
        "DB_NAME",
        "lectores_agua",
    ),
    "collation": os.getenv(
        "DB_COLLATION",
        "utf8mb4_general_ci",
    ),
    "charset": "utf8mb4",
}


class Config:
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "solo-desarrollo-cambiar-en-produccion",
    )

    UPLOAD_FOLDER = os.getenv(
        "UPLOAD_FOLDER",
        "app/static/uploads",
    )

    MAX_CONTENT_LENGTH = int(
        os.getenv(
            "MAX_CONTENT_LENGTH",
            str(20 * 1024 * 1024),
        )
    )

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    SESSION_COOKIE_SECURE = environment_flag(
        "SESSION_COOKIE_SECURE",
        "0",
    )

    PREFERRED_URL_SCHEME = os.getenv(
        "PREFERRED_URL_SCHEME",
        "http",
    )
