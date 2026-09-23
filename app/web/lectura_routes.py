from flask import (
    Blueprint,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required

from app.infrastructure.file_storage import save_uploaded_file
from app.repositories.inmueble_repository import (
    get_inmueble_by_codigo,
    get_inmueble_id_by_codigo,
)

from app.repositories.lectura_repository import (
    delete_lectura,
    get_lectura_by_id,
    get_lecturas,
    update_lectura,
)

lecturas_bp = Blueprint('lecturas', __name__)

@lecturas_bp.route('/lecturas')
@login_required
def listar_lecturas():
    codigo_inmueble = request.args.get('codigo_inmueble')
    lecturas = get_lecturas(codigo_inmueble)

    return render_template(
        'lecturas.html',
        lecturas=lecturas,
    )


@lecturas_bp.route('/lecturas/<int:lectura_id>')
@login_required
def detalle_lectura(lectura_id):
    lectura = get_lectura_by_id(lectura_id)

    if lectura:
        return render_template(
            'detalle_lectura.html',
            lectura=lectura,
        )

    return jsonify(
        {"error": f"No se encontró la lectura con ID {lectura_id}"}
    ), 404


@lecturas_bp.route('/lecturas/<int:lectura_id>/editar')
@login_required
def editar_lectura(lectura_id):
    lectura = get_lectura_by_id(lectura_id)

    if lectura:
        return render_template(
            'editar_lectura.html',
            lectura=lectura,
        )

    return jsonify(
        {"error": f"No se encontró la lectura con ID {lectura_id}"}
    ), 404


@lecturas_bp.route(
    '/lecturas/<int:lectura_id>/actualizar',
    methods=['POST'],
)
@login_required
def actualizar_lectura(lectura_id):
    codigo_inmueble = request.form.get('codigo_inmueble')
    lectura = request.form.get('lectura')
    observacion = request.form.get('observacion')
    mes_proceso = request.form.get('mes_proceso')

    coordenada_x = (
        request.form.get('coordenada_x') or ''
    ).strip() or None

    coordenada_y = (
        request.form.get('coordenada_y') or ''
    ).strip() or None

    foto_contador = request.files.get('foto_contador')
    foto_inmueble = request.files.get('foto_inmueble')

    foto_contador_actual = request.form.get('foto_contador_actual')
    foto_inmueble_actual = request.form.get('foto_inmueble_actual')

    if get_inmueble_id_by_codigo(codigo_inmueble) is None:
        return jsonify(
            {
                "error": (
                    "No se encontró el inmueble con código "
                    f"{codigo_inmueble}"
                )
            }
        ), 404

    if foto_contador:
        path_contador = save_uploaded_file(
            foto_contador,
            current_app.config['UPLOAD_FOLDER'],
        )
    else:
        path_contador = foto_contador_actual

    if foto_inmueble:
        path_inmueble = save_uploaded_file(
            foto_inmueble,
            current_app.config['UPLOAD_FOLDER'],
        )
    else:
        path_inmueble = foto_inmueble_actual

    resultado = update_lectura(
        lectura_id=lectura_id,
        lectura=lectura,
        observacion=observacion,
        mes_proceso=mes_proceso,
        coordenada_x=coordenada_x,
        coordenada_y=coordenada_y,
        path_contador=path_contador,
        path_inmueble=path_inmueble,
    )

    if resultado is None:
        return jsonify(
            {"error": "No se pudo actualizar la lectura"}
        ), 500

    return redirect(
        url_for(
            'lecturas.detalle_lectura',
            lectura_id=lectura_id,
        )
    )

@lecturas_bp.route('/lecturas/<int:lectura_id>/eliminar')
@login_required
def eliminar_lectura(lectura_id):
    resultado = delete_lectura(lectura_id)

    if resultado is None:
        return jsonify(
            {"error": "No se pudo eliminar la lectura"}
        ), 500

    return redirect(
        url_for(
            'lecturas.listar_lecturas',
            message='Lectura eliminada correctamente',
            message_type='success',
        )
    )


@lecturas_bp.route('/lectura/<codigo>', methods=['GET'])
@login_required
def mostrar_lectura(codigo):
    inmueble = get_inmueble_by_codigo(codigo)

    if inmueble:
        return render_template(
            'lectura.html',
            inmueble=inmueble,
        )

    return redirect(
        url_for(
            'errores.registrar_error',
            codigo=codigo,
        )
    )
