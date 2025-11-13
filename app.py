from flask import Flask, render_template, request, redirect, url_for, flash, session
from funciones_crud import (
    agregar_cliente,
    listar_clientes,
    obtener_cliente,
    actualizar_cliente,
    eliminar_cliente,
    buscar_clientes,
    filtrar_clientes_por_tipo,
    verificar_identificacion_unica
)
from conexion import conectar  # para validar usuarios
from functools import wraps

app = Flask(__name__)
app.secret_key = "mi_clave_secreta"

# ---------------------------------------
# Decorador para proteger rutas
# ---------------------------------------
def login_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('⚠️ Debes iniciar sesión primero', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------------------
# Login
# ---------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email=%s AND password=%s", (email, password))
        usuario = cursor.fetchone()
        cursor.close()
        conexion.close()

        if usuario:
            # Guardar datos en la sesión
            session['usuario_id'] = usuario['id']
            session['usuario_nombre'] = usuario['nombre']
            session['rol'] = usuario.get('rol', 'cliente')  # Si no tiene rol, asigna 'cliente'

            flash('✅ Inicio de sesión exitoso.', 'success')

            # Redirección según el rol
            if session['rol'] == 'admin':
                return redirect(url_for('crud'))
            else:
                return redirect(url_for('perfil_cliente'))
        else:
            flash('❌ Usuario o contraseña incorrectos.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

# ---------------------------------------
# Página inicial → redirige según sesión
# ---------------------------------------
@app.route('/')
def inicio():
    if 'usuario_id' in session:
        rol = session.get('rol', None)
        if rol == 'admin':
            return redirect(url_for('crud'))
        elif rol == 'cliente':
            return redirect(url_for('perfil_cliente'))
    return redirect(url_for('login'))

# ---------------------------------------
# Registro cliente
# ---------------------------------------
@app.route('/registro_cliente', methods=['GET', 'POST'])
def registro_cliente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']

        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email=%s", (email,))
        if cursor.fetchone()[0] > 0:
            flash('⚠️ Este correo ya está registrado', 'error')
            cursor.close()
            conexion.close()
            return redirect(url_for('registro_cliente'))

        cursor.execute("INSERT INTO usuarios (nombre, email, password, rol) VALUES (%s, %s, %s, 'cliente')",
                       (nombre, email, password))
        conexion.commit()
        cursor.close()
        conexion.close()

        flash('✅ Registro exitoso. Ahora inicia sesión.', 'success')
        return redirect(url_for('login'))

    return render_template('registro_cliente.html')

# ---------------------------------------
# Logout
# ---------------------------------------
@app.route('/logout')
def logout():
    session.clear()
    flash('✅ Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('login'))

# ---------------------------------------
# Perfil cliente
# ---------------------------------------
@app.route('/perfil_cliente')
@login_requerido
def perfil_cliente():
    rol = session.get('rol', None)
    if rol != 'cliente':
        flash('⚠️ Solo los clientes pueden acceder aquí.', 'error')
        return redirect(url_for('inicio'))
    
    nombre = session.get('usuario_nombre', 'Usuario')
    return render_template('perfil_cliente.html', usuario=nombre)

# ----------------------------------------------------------------------
# CRUD solo para ADMIN
# ----------------------------------------------------------------------
@app.route('/crud')
@login_requerido
def crud():
    rol = session.get('rol', None)
    if rol != 'admin':
        flash('⚠️ Solo los administradores pueden acceder al CRUD.', 'error')
        return redirect(url_for('perfil_cliente'))

    clientes = listar_clientes()
    return render_template("listar.html", clientes=clientes, active_page="listar")

# ----------------------------------------------------------------------
# Buscar clientes
# ----------------------------------------------------------------------
@app.route('/buscar', methods=['GET'])
def buscar():
    filtro_texto = request.args.get('filtro', '')
    filtro_tipo = request.args.get('tipo', '') 
    
    if filtro_tipo in ['NATURAL', 'LEGAL']:
        clientes = filtrar_clientes_por_tipo(filtro_tipo)
    elif filtro_texto:
        clientes = buscar_clientes(filtro_texto)
    else:
        clientes = listar_clientes()
        
    return render_template('listar.html', 
                           clientes=clientes, 
                           filtro=filtro_texto, 
                           active_page="listar", 
                           filtro_tipo=filtro_tipo)

# ----------------------------------------------------------------------
# Crear clientes
# ----------------------------------------------------------------------
@app.route('/registro')
def registro():
    return render_template("agregar.html", active_page="agregar")

@app.route('/agregar', methods=['POST'])
def agregar():
    person_type = request.form['person_type']
    phone = request.form['phone']
    email = request.form['email']
    city = request.form['city']
    address = request.form['address']
    
    comun_data = (phone, email, city, address)
    id_card_number = None
    ruc = None
    nombre_identificacion = ""
    valor_identificacion = ""
    full_name = None
    company_name = None
    
    if person_type == 'NATURAL':
        id_card_number = request.form['id_card_number']
        nombre_identificacion = "Cédula/DNI"
        valor_identificacion = id_card_number
        full_name = request.form['full_name']
        especifica_data = (id_card_number, full_name)
        
    elif person_type == 'LEGAL':
        ruc = request.form['ruc']
        nombre_identificacion = "RUC"
        valor_identificacion = ruc
        company_name = request.form['company_name']
        industry = request.form['industry']
        codigo_ciiu = request.form['codigo_ciiu'] 
        especifica_data = (ruc, company_name, industry, codigo_ciiu) 
    
    if verificar_identificacion_unica(id_card_number, ruc):
        flash(f'⚠️ Error: El número de {nombre_identificacion} "{valor_identificacion}" ya está registrado.', 'error')
        return redirect(url_for('registro'))

    try:
        if person_type == 'NATURAL':
            agregar_cliente(person_type, comun_data, especifica_data)
            flash(f'✅ Persona Natural {full_name} agregada con éxito.')
        elif person_type == 'LEGAL':
            agregar_cliente(person_type, comun_data, especifica_data)
            flash(f'✅ Empresa {company_name} agregada con éxito.')
    except Exception as e:
        flash(f'❌ Error al agregar cliente: {e}', 'error')
        
    return redirect(url_for('crud'))

# ----------------------------------------------------------------------
# Editar cliente
# ----------------------------------------------------------------------
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    cliente = obtener_cliente(id) 
    if not cliente:
        flash("Cliente no encontrado.", "error")
        return redirect(url_for('crud'))

    if request.method == 'POST':
        person_type = request.form['person_type'] 
        phone = request.form['phone']
        email = request.form['email']
        city = request.form['city']
        address = request.form['address']
        
        comun_data = (phone, email, city, address, id) 
        
        try:
            if person_type == 'NATURAL':
                full_name = request.form['full_name']
                id_card_number = request.form['id_card_number']
                especifica_data = (id_card_number, full_name, id) 
                actualizar_cliente(id, person_type, comun_data, especifica_data)
                flash(f'✅ Persona Natural {full_name} actualizada con éxito.')
            elif person_type == 'LEGAL':
                company_name = request.form['company_name']
                ruc = request.form['ruc']
                industry = request.form['industry']
                codigo_ciiu = request.form['codigo_ciiu'] 
                especifica_data = (ruc, company_name, industry, codigo_ciiu, id) 
                actualizar_cliente(id, person_type, comun_data, especifica_data)
                flash(f'✅ Empresa {company_name} actualizada con éxito.')
        except Exception as e:
            flash(f'❌ Error al actualizar cliente {id}: {e}', 'error')
            
        return redirect(url_for('crud'))

    return render_template('editar.html', cliente=cliente, active_page='listar')

# ----------------------------------------------------------------------
# Ver detalle
# ----------------------------------------------------------------------
@app.route('/ver/<int:id>')
def ver_cliente(id):
    cliente = obtener_cliente(id) 
    if not cliente:
        flash("Cliente no encontrado.", "error")
        return redirect(url_for('crud'))
    return render_template('ver_cliente.html', cliente=cliente, active_page='listar')

# ----------------------------------------------------------------------
# Eliminar cliente
# ----------------------------------------------------------------------
@app.route('/eliminar/<int:id>')
def eliminar(id):
    try:
        eliminar_cliente(id)
        flash(f'✅ Cliente con ID {id} eliminado con éxito.')
    except Exception as e:
        flash(f'❌ Error al intentar eliminar el cliente {id}: {e}', 'error')
    return redirect(url_for('crud'))

# ----------------------------------------------------------------------
# Enviar correo
# ----------------------------------------------------------------------
@app.route('/enviar_correo')
def enviar_correo():
    return render_template('enviar_correo.html')

@app.route('/')
def index():
    return redirect(url_for('listar_clientes'))


# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)


































