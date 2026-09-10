# app/main.py
from flask import Flask, jsonify, request, render_template, redirect, url_for, session, flash, send_from_directory
from app.models.database import execute_query
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui_cambiala_por_una_segura'

# Configuración para subir archivos
UPLOAD_FOLDER = 'app/static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Clase de usuario para Flask-Login
class User(UserMixin):
    def __init__(self, id, nombre, correo, rol):
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.rol = rol

@login_manager.user_loader
def load_user(user_id):
    query = "SELECT id, nombre, correo, rol FROM usuarios WHERE id = %s"
    usuario = execute_query(query, (user_id,), fetch=True)
    if usuario:
        return User(usuario[0]['id'], usuario[0]['nombre'], usuario[0]['correo'], usuario[0]['rol'])
    return None

@app.route('/')
def root():
    if current_user.is_authenticated:
        return render_template('panel.html', usuario=current_user)
    return redirect(url_for('login'))

@app.route('/index')
@login_required
def buscar_inmueble():
    return render_template('index.html')

@app.route('/lecturas')
@login_required
def listar_lecturas():
    codigo_inmueble = request.args.get('codigo_inmueble')
    if codigo_inmueble:
        query = """
        SELECT
            l.id, i.codigo_tarjeta, i.nombre AS nombre_inmueble, i.direccion,
            u.nombre AS nombre_usuario, l.fecha_lectura, l.lectura, l.observacion,
            l.mes_proceso, l.foto_contador, l.foto_inmueble,
            l.coordenada_x, l.coordenada_y
        FROM lecturas l
        JOIN inmuebles i ON l.inmueble_id = i.id
        JOIN usuarios u ON l.usuario_id = u.id
        WHERE i.codigo_tarjeta LIKE %s
        ORDER BY l.fecha_lectura DESC
        """
        params = (f"%{codigo_inmueble}%",)
    else:
        query = """
        SELECT
            l.id, i.codigo_tarjeta, i.nombre AS nombre_inmueble, i.direccion,
            u.nombre AS nombre_usuario, l.fecha_lectura, l.lectura, l.observacion,
            l.mes_proceso, l.foto_contador, l.foto_inmueble,
            l.coordenada_x, l.coordenada_y
        FROM lecturas l
        JOIN inmuebles i ON l.inmueble_id = i.id
        JOIN usuarios u ON l.usuario_id = u.id
        ORDER BY l.fecha_lectura DESC
        """
        params = ()
    lecturas = execute_query(query, params, fetch=True)
    return render_template('lecturas.html', lecturas=lecturas)

@app.route('/lecturas/<int:lectura_id>')
@login_required
def detalle_lectura(lectura_id):
    query = """
    SELECT
        l.id, i.codigo_tarjeta, i.nombre AS nombre_inmueble, i.direccion,
        u.nombre AS nombre_usuario, l.fecha_lectura, l.lectura, l.observacion,
        l.mes_proceso, l.foto_contador, l.foto_inmueble,
        l.coordenada_x, l.coordenada_y
    FROM lecturas l
    JOIN inmuebles i ON l.inmueble_id = i.id
    JOIN usuarios u ON l.usuario_id = u.id
    WHERE l.id = %s
    """
    lectura = execute_query(query, (lectura_id,), fetch=True)
    if lectura:
        return render_template('detalle_lectura.html', lectura=lectura[0])
    return jsonify({"error": f"No se encontró la lectura con ID {lectura_id}"}), 404

@app.route('/lecturas/<int:lectura_id>/editar')
@login_required
def editar_lectura(lectura_id):
    query = """
    SELECT
        l.id, i.codigo_tarjeta, i.nombre AS nombre_inmueble, i.direccion,
        u.nombre AS nombre_usuario, l.fecha_lectura, l.lectura, l.observacion,
        l.mes_proceso, l.foto_contador, l.foto_inmueble,
        l.coordenada_x, l.coordenada_y
    FROM lecturas l
    JOIN inmuebles i ON l.inmueble_id = i.id
    JOIN usuarios u ON l.usuario_id = u.id
    WHERE l.id = %s
    """
    lectura = execute_query(query, (lectura_id,), fetch=True)
    if lectura:
        return render_template('editar_lectura.html', lectura=lectura[0])
    return jsonify({"error": f"No se encontró la lectura con ID {lectura_id}"}), 404

@app.route('/lecturas/<int:lectura_id>/actualizar', methods=['POST'])
@login_required
def actualizar_lectura(lectura_id):
    codigo_inmueble = request.form.get('codigo_inmueble')
    lectura = request.form.get('lectura')
    observacion = request.form.get('observacion')
    mes_proceso = request.form.get('mes_proceso')
    coordenada_x = request.form.get('coordenada_x')
    coordenada_y = request.form.get('coordenada_y')
    foto_contador = request.files.get('foto_contador')
    foto_inmueble = request.files.get('foto_inmueble')
    foto_contador_actual = request.form.get('foto_contador_actual')
    foto_inmueble_actual = request.form.get('foto_inmueble_actual')

    query_inmueble = "SELECT id FROM inmuebles WHERE codigo_tarjeta = %s"
    inmueble = execute_query(query_inmueble, (codigo_inmueble,), fetch=True)
    if not inmueble:
        return jsonify({"error": f"No se encontró el inmueble con código {codigo_inmueble}"}), 404
    inmueble_id = inmueble[0]['id']

    if foto_contador:
        filename_contador = secure_filename(foto_contador.filename)
        path_contador = os.path.join(app.config['UPLOAD_FOLDER'], filename_contador)
        foto_contador.save(path_contador)
    else:
        path_contador = foto_contador_actual

    if foto_inmueble:
        filename_inmueble = secure_filename(foto_inmueble.filename)
        path_inmueble = os.path.join(app.config['UPLOAD_FOLDER'], filename_inmueble)
        foto_inmueble.save(path_inmueble)
    else:
        path_inmueble = foto_inmueble_actual

    query_lectura = """
    UPDATE lecturas
    SET lectura = %s, observacion = %s, mes_proceso = %s,
        coordenada_x = %s, coordenada_y = %s,
        foto_contador = %s, foto_inmueble = %s
    WHERE id = %s
    """
    params = (lectura, observacion, mes_proceso, coordenada_x, coordenada_y, path_contador, path_inmueble, lectura_id)
    execute_query(query_lectura, params)
    return redirect(url_for('detalle_lectura', lectura_id=lectura_id))

@app.route('/lecturas/<int:lectura_id>/eliminar')
@login_required
def eliminar_lectura(lectura_id):
    query = "DELETE FROM lecturas WHERE id = %s"
    execute_query(query, (lectura_id,))
    return redirect(url_for('listar_lecturas', message="Lectura eliminada correctamente", message_type="success"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        contrasena = request.form.get('contrasena')
        query = "SELECT id, nombre, correo, contrasena, rol FROM usuarios WHERE nombre = %s"
        usuario = execute_query(query, (nombre,), fetch=True)
        if usuario and check_password_hash(usuario[0]['contrasena'], contrasena):
            user = User(usuario[0]['id'], usuario[0]['nombre'], usuario[0]['correo'], usuario[0]['rol'])
            login_user(user)
            return redirect(url_for('root'))
        else:
            return render_template('login.html', error="Nombre de usuario o contraseña incorrectos")
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        contrasena = request.form.get('contrasena')
        rol = request.form.get('rol')
        contrasena_cifrada = generate_password_hash(contrasena)
        query = "INSERT INTO usuarios (nombre, correo, contrasena, rol) VALUES (%s, %s, %s, %s)"
        params = (nombre, correo, contrasena_cifrada, rol)
        try:
            execute_query(query, params)
            return redirect(url_for('login'))
        except Exception as e:
            return render_template('registro.html', error=f"Error al registrar el usuario: {str(e)}")
    return render_template('registro.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- RUTAS PARA INMUEBLES CON ERRORES ---
@app.route('/inmuebles_errores')
@login_required
def listar_errores():
    codigo_tarjeta = request.args.get('codigo_tarjeta')
    if codigo_tarjeta:
        query = """
        SELECT
            ie.id,
            ie.codigo_tarjeta,
            ie.direccion_servicio,
            ie.ruta,
            ie.tarifa,
            ie.contador_agua,
            ie.foto_contador,
            ie.foto_inmueble,
            ie.coordenada_x,
            ie.coordenada_y,
            ie.observaciones,
            ie.fecha_registro,
            u.nombre AS nombre_usuario
        FROM inmuebles_errores ie
        LEFT JOIN usuarios u ON ie.usuario_id = u.id
        WHERE ie.codigo_tarjeta LIKE %s
        ORDER BY ie.fecha_registro DESC
        """
        params = (f"%{codigo_tarjeta}%",)
    else:
        query = """
        SELECT
            ie.id,
            ie.codigo_tarjeta,
            ie.direccion_servicio,
            ie.ruta,
            ie.tarifa,
            ie.contador_agua,
            ie.foto_contador,
            ie.foto_inmueble,
            ie.coordenada_x,
            ie.coordenada_y,
            ie.observaciones,
            ie.fecha_registro,
            u.nombre AS nombre_usuario
        FROM inmuebles_errores ie
        LEFT JOIN usuarios u ON ie.usuario_id = u.id
        ORDER BY ie.fecha_registro DESC
        """
        params = ()
    errores = execute_query(query, params, fetch=True)
    return render_template('errores.html', errores=errores)

@app.route('/inmuebles_errores/registrar/<codigo>')
@login_required
def registrar_error(codigo):
    return render_template('registrar_error.html', codigo=codigo)

@app.route('/inmuebles_errores', methods=['POST'])
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

    path_contador = None
    path_inmueble = None

    if foto_contador:
        filename_contador = secure_filename(foto_contador.filename)
        path_contador = os.path.join(app.config['UPLOAD_FOLDER'], filename_contador)
        foto_contador.save(path_contador)

    if foto_inmueble:
        filename_inmueble = secure_filename(foto_inmueble.filename)
        path_inmueble = os.path.join(app.config['UPLOAD_FOLDER'], filename_inmueble)
        foto_inmueble.save(path_inmueble)

    query = """
    INSERT INTO inmuebles_errores
    (codigo_tarjeta, direccion_servicio, ruta, tarifa, contador_agua, foto_contador, foto_inmueble, coordenada_x, coordenada_y, observaciones, usuario_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        codigo_tarjeta,
        direccion_servicio,
        ruta,
        tarifa,
        contador_agua,
        path_contador,
        path_inmueble,
        coordenada_x,
        coordenada_y,
        observaciones,
        usuario_id
    )
    execute_query(query, params)
    return redirect(url_for('listar_errores', message="Inmueble con error registrado correctamente", message_type="success"))

@app.route('/inmuebles_errores/<int:error_id>')
@login_required
def detalle_error(error_id):
    query = """
    SELECT
        ie.id,
        ie.codigo_tarjeta,
        ie.direccion_servicio,
        ie.ruta,
        ie.tarifa,
        ie.contador_agua,
        ie.foto_contador,
        ie.foto_inmueble,
        ie.coordenada_x,
        ie.coordenada_y,
        ie.observaciones,
        ie.fecha_registro,
        u.nombre AS nombre_usuario
    FROM inmuebles_errores ie
    LEFT JOIN usuarios u ON ie.usuario_id = u.id
    WHERE ie.id = %s
    """
    error = execute_query(query, (error_id,), fetch=True)
    if error:
        return render_template('detalle_error.html', error=error[0])
    return jsonify({"error": f"No se encontró el registro con ID {error_id}"}), 404

@app.route('/inmuebles_errores/<int:error_id>/editar')
@login_required
def editar_error(error_id):
    query = """
    SELECT
        ie.id,
        ie.codigo_tarjeta,
        ie.direccion_servicio,
        ie.ruta,
        ie.tarifa,
        ie.contador_agua,
        ie.foto_contador,
        ie.foto_inmueble,
        ie.coordenada_x,
        ie.coordenada_y,
        ie.observaciones
    FROM inmuebles_errores ie
    WHERE ie.id = %s
    """
    error = execute_query(query, (error_id,), fetch=True)
    if error:
        return render_template('editar_error.html', error=error[0])
    return jsonify({"error": f"No se encontró el registro con ID {error_id}"}), 404

@app.route('/inmuebles_errores/<int:error_id>/actualizar', methods=['POST'])
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
    foto_contador_actual = request.form.get('foto_contador_actual')
    foto_inmueble_actual = request.form.get('foto_inmueble_actual')

    if foto_contador:
        filename_contador = secure_filename(foto_contador.filename)
        path_contador = os.path.join(app.config['UPLOAD_FOLDER'], filename_contador)
        foto_contador.save(path_contador)
    else:
        path_contador = foto_contador_actual

    if foto_inmueble:
        filename_inmueble = secure_filename(foto_inmueble.filename)
        path_inmueble = os.path.join(app.config['UPLOAD_FOLDER'], filename_inmueble)
        foto_inmueble.save(path_inmueble)
    else:
        path_inmueble = foto_inmueble_actual

    query = """
    UPDATE inmuebles_errores
    SET
        codigo_tarjeta = %s,
        direccion_servicio = %s,
        ruta = %s,
        tarifa = %s,
        contador_agua = %s,
        foto_contador = %s,
        foto_inmueble = %s,
        coordenada_x = %s,
        coordenada_y = %s,
        observaciones = %s
    WHERE id = %s
    """
    params = (
        codigo_tarjeta,
        direccion_servicio,
        ruta,
        tarifa,
        contador_agua,
        path_contador,
        path_inmueble,
        coordenada_x,
        coordenada_y,
        observaciones,
        error_id
    )
    execute_query(query, params)
    return redirect(url_for('detalle_error', error_id=error_id))

@app.route('/inmuebles_errores/<int:error_id>/eliminar')
@login_required
def eliminar_error(error_id):
    query = "DELETE FROM inmuebles_errores WHERE id = %s"
    execute_query(query, (error_id,))
    return redirect(url_for('listar_errores', message="Registro eliminado correctamente", message_type="success"))

# --- RUTA PARA MOSTRAR LECTURA O REDIRIGIR A REGISTRAR ERROR ---
@app.route('/lectura/<codigo>', methods=['GET'])
@login_required
def mostrar_lectura(codigo):
    query = "SELECT * FROM inmuebles WHERE codigo_tarjeta = %s"
    inmueble = execute_query(query, (codigo,), fetch=True)
    if inmueble:
        return render_template('lectura.html', inmueble=inmueble[0])
    else:
        # Si el código no existe, redirigir a registrar_error
        return redirect(url_for('registrar_error', codigo=codigo))

if __name__ == '__main__':
    app.run(debug=True)