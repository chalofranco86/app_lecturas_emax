from flask import (
    Blueprint,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_login import current_user, login_required
from datetime import datetime, datetime as dt_local, timezone
from uuid import uuid4

from app.infrastructure.file_storage import save_uploaded_file
from app.repositories.inmueble_repository import (
    get_inmueble_by_contador,
    get_inmueble_by_codigo,
    get_inmueble_id_by_codigo,
    get_rutas,
)
from app.repositories.lectura_repository import (
    delete_lectura,
    get_lectura_anterior,
    get_lectura_by_id,
    get_lecturas,
    update_lectura,
)
from app.services.lectura_service import create_lectura
from app.services.reporte_service import generar_excel_lecturas


lecturas_bp = Blueprint('lecturas', __name__)


@lecturas_bp.route("/lecturas")
@login_required
def listar_lecturas():
    lecturas = get_lecturas(
        codigo_inmueble=request.args.get("codigo_inmueble"),
        mes_proceso=request.args.get("mes_proceso"),
        ruta=request.args.get("ruta"),
        correlativo=request.args.get("correlativo"),
    )
    return render_template("lecturas.html", lecturas=lecturas)


@lecturas_bp.route('/lecturas', methods=['POST'])
@login_required
def registrar_lectura():
    data = request.form.to_dict()
    data['client_uuid'] = str(uuid4())
    data['fecha_captura'] = datetime.now(timezone.utc).isoformat()

    resultado = create_lectura(
        data=data,
        foto_contador=request.files.get('foto_contador'),
        foto_inmueble=request.files.get('foto_inmueble'),
        usuario_id=current_user.id,
        upload_folder=current_app.config['UPLOAD_FOLDER'],
    )

    if not resultado['ok']:
        inmueble = get_inmueble_by_codigo(data.get('codigo_inmueble'))

        # 🔑 Conservar la lectura anterior en el re-render de errores
        lectura_anterior = None
        if inmueble:
            lectura_anterior = get_lectura_anterior(inmueble['id'])

        return render_template(
            'lectura.html',
            inmueble=inmueble,
            lectura_anterior=lectura_anterior,   # ← nuevo
            error_message=resultado.get('message'),
            validation_errors=resultado.get('errors', {}),
        ), 400

    lectura = resultado.get('data')
    if not lectura or not lectura.get('id'):
        return jsonify(
            {'error': 'La lectura se guardó, pero no se pudo abrir su detalle'}
        ), 500

    return redirect(
        url_for(
            'lecturas.detalle_lectura',
            lectura_id=lectura['id'],
        )
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
        lectura_anterior = get_lectura_anterior(inmueble['id'])

        return render_template(
            'lectura.html',
            inmueble=inmueble,
            lectura_anterior=lectura_anterior,
        )

    return redirect(url_for('errores.registrar_error', codigo=codigo))


@lecturas_bp.route('/lectura/nit/<contador>', methods=['GET'])
@login_required
def mostrar_lectura_por_contador(contador):
    inmueble = get_inmueble_by_contador(contador)

    if inmueble:
        # 🔑 También aquí la lectura anterior
        lectura_anterior = get_lectura_anterior(inmueble['id'])

        return render_template(
            'lectura.html',
            inmueble=inmueble,
            lectura_anterior=lectura_anterior,   # ← nuevo
        )

    return redirect(
        url_for(
            'errores.registrar_error',
            codigo=contador,
        )
    )


# --- REPORTES EXCEL ---

# Opción 1: Reporte con los filtros aplicados en la búsqueda
@lecturas_bp.route("/lecturas/exportar/filtrado", methods=["GET"])
@login_required
def exportar_lecturas_filtrado():
    codigo_inmueble = request.args.get("codigo_inmueble")
    mes_proceso = request.args.get("mes_proceso")
    ruta = request.args.get("ruta")
    correlativo = request.args.get("correlativo")

    lecturas = get_lecturas(
        codigo_inmueble=codigo_inmueble,
        mes_proceso=mes_proceso,
        ruta=ruta,
        correlativo=correlativo,
    )

    if not lecturas:
        return redirect(url_for("lecturas.listar_lecturas",
                                message="No hay datos para exportar con esos filtros",
                                message_type="error"))

    excel = generar_excel_lecturas(lecturas, nombre_hoja="Lecturas Filtradas")

    fecha_actual = dt_local.now().strftime("%Y%m%d_%H%M")
    nombre_archivo = f"lecturas_filtradas_{fecha_actual}.xlsx"

    return send_file(
        excel,
        as_attachment=True,
        download_name=nombre_archivo,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# Opción 2: Reporte de TODAS las lecturas por ruta
@lecturas_bp.route("/lecturas/exportar/por_ruta", methods=["GET"])
@login_required
def exportar_lecturas_por_ruta():
    ruta = request.args.get("ruta")
    correlativo = request.args.get("correlativo")

    lecturas = get_lecturas(
        ruta=ruta,
        correlativo=correlativo,
    )

    if not lecturas:
        return redirect(url_for("lecturas.listar_lecturas",
                                message="No hay datos para exportar con esos parámetros",
                                message_type="error"))

    excel = generar_excel_lecturas(lecturas, nombre_hoja=f"Ruta {ruta or 'Todas'}")

    fecha_actual = dt_local.now().strftime("%Y%m%d_%H%M")
    sufijo_ruta = (ruta or "todas").replace(" ", "_")
    nombre_archivo = f"lecturas_ruta_{sufijo_ruta}_{fecha_actual}.xlsx"

    return send_file(
        excel,
        as_attachment=True,
        download_name=nombre_archivo,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )