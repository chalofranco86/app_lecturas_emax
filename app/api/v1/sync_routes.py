from flask import Blueprint


api_sync_bp = Blueprint(
    "api_sync",
    __name__,
    url_prefix="/sync",
)
