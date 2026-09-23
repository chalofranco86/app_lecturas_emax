from flask import (
    Blueprint,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from app.infrastructure.file_storage import save_uploaded_file
from app.repositories.error_repository import (
    delete_error,
    get_error_by_id,
    get_errores,
    insert_error,
    update_error,
)


errores_bp = Blueprint('errores', __name__)


def _normalize_optional_path(value):
    value = str(value or "").strip()

    if value.lower() in {"", "none", "null"}:
        return None

    return value


@errores_bp.route('/inmuebles_errores')
@login_required
def listar_errores():
    codigo_tarjeta = request.args.get('codigo_tarjeta')
    errores = get_errores(codigo_tarjeta)

    return render_template(
        'errores.html',
        errores=errores,
    )


@errores_bp.route(
    '/inmuebles_errores/registrar/<codigo>'
)
@login_required
def registrar_error(codigo):
    return render_template(
        'registrar_error.html',
        codigo=codigo,
    )


@errores_bp.route(
    '/inmuebles_errores/<int:error_id>'
)
@login_required
def detalle_error(error_id):
    error = get_error_by_id(error_id)

    if error:
        return render_template(
            'detalle_error.html',
            error=error,
        )

    return jsonify(
        {"error": f"No se encontró el registro con ID {error_id}"}
    ), 404


@errores_bp.route(
    '/inmuebles_errores/<int:error_id>/editar'
)
@login_required
def editar_error(error_id):
    error = get_error_by_id(error_id)

    if error:
        return render_template(
            'editar_error.html',
            error=error,
        )

    return jsonify(
        {"error": f"No se encontró el registro con ID {error_id}"}
    ), 404


@errores_bp.route(
        '/inmuebles_errores', methods=['POST'])
@login_required
def add_error():
    codigo_tarjeta = request.form.get('codigo_tarjeta')
    direccion_servicio = request.form.get('direccion_servicio')
    ruta = request.form.get('ruta')
    tarifa = request.form.get('tarifa')
    contador_agua = request.form.get('contador_agua')
    observaciones = request.form.get('observaciones')
    coordenada_x = request.form.get('coordenada_x')
    coordenada_y = request.form.get('coordenada_y')
    usuario_id = current_user.id

    foto_contador = request.files.get('foto_contador')
    foto_inmueble = request.files.get('foto_inmueble')

    path_contador = save_uploaded_file(
        foto_contador,
        current_app.config['UPLOAD_FOLDER'],
    )

    path_inmueble = save_uploaded_file(
        foto_inmueble,
        current_app.config['UPLOAD_FOLDER'],
    )

    resultado = insert_error(
        codigo_tarjeta=codigo_tarjeta,
        direccion_servicio=direccion_servicio,
        ruta=ruta,
        tarifa=tarifa,
        contador_agua=contador_agua,
        path_contador=path_contador,
        path_inmueble=path_inmueble,
        coordenada_x=coordenada_x,
        coordenada_y=coordenada_y,
        observaciones=observaciones,
        usuario_id=usuario_id,
    )

    if resultado is None:
        return jsonify(
            {"error": "No se pudo registrar el inmueble con error"}
        ), 500

    return redirect(
        url_for(
            'errores.listar_errores',
            message="Inmueble con error registrado correctamente",
            message_type="success",
        )
    )


@errores_bp.route(
        '/inmuebles_errores/<int:error_id>/actualizar', methods=['POST'])
@login_required
def actualizar_error(error_id):
    codigo_tarjeta = request.form.get('codigo_tarjeta')
    direccion_servicio = request.form.get('direccion_servicio')
    ruta = request.form.get('ruta')
    tarifa = request.form.get('tarifa')
    contador_agua = request.form.get('contador_agua')
    observaciones = request.form.get('observaciones')
    coordenada_x = request.form.get('coordenada_x')
    coordenada_y = request.form.get('coordenada_y')

    foto_contador = request.files.get('foto_contador')
    foto_inmueble = request.files.get('foto_inmueble')
    foto_contador_actual = _normalize_optional_path(
        request.form.get("foto_contador_actual")
    )
    foto_inmueble_actual = _normalize_optional_path(
        request.form.get("foto_inmueble_actual")
    )

    if foto_contador:
        path_contador = save_uploaded_file(
            foto_contador,
            current_app.config['UPLOAD_FOLDER'],
            foto_contador_actual,
        )

    else:
        path_contador = foto_contador_actual

    if foto_inmueble:
        path_inmueble = save_uploaded_file(
            foto_inmueble,
            current_app.config['UPLOAD_FOLDER'],
            foto_inmueble_actual,
        )
    else:
        path_inmueble = foto_inmueble_actual

    resultado = update_error(
        error_id=error_id,
        codigo_tarjeta=codigo_tarjeta,
        direccion_servicio=direccion_servicio,
        ruta=ruta,
        tarifa=tarifa,
        contador_agua=contador_agua,
        path_contador=path_contador,
        path_inmueble=path_inmueble,
        coordenada_x=coordenada_x,
        coordenada_y=coordenada_y,
        observaciones=observaciones,
    )

    if resultado is None:
        return jsonify(
            {"error": "No se pudo actualizar el inmueble con error"}
        ), 500

    return redirect(url_for('errores.detalle_error', error_id=error_id))


@errores_bp.route(
    '/inmuebles_errores/<int:error_id>/eliminar'
)
@login_required
def eliminar_error(error_id):
    resultado = delete_error(error_id)

    if resultado is None:
        return jsonify(
            {"error": "No se pudo eliminar el registro"}
        ), 500

    return redirect(url_for(
        'errores.listar_errores',
        message='Registro eliminado correctamente',
        message_type='success',
    ))
