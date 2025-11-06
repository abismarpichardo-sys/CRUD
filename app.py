from flask import Flask, render_template, request, redirect, url_for, flash
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

app = Flask(__name__)
app.secret_key = "mi_clave_secreta" 

# ----------------------------------------------------------------------
# 1. Rutas de Listado y Búsqueda (READ)
# ----------------------------------------------------------------------

@app.route('/')
def index():
    clientes = listar_clientes()
    # La lista de clientes se envía a listar.html (Vista simplificada)
    return render_template("listar.html", clientes=clientes, active_page="listar")

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
# 2. Rutas de Creación (CREATE)
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
    
    # --- 1. PREPARAR DATOS Y VALIDAR UNICIDAD ---
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
        flash(f'⚠️ Error: El número de {nombre_identificacion} "{valor_identificacion}" ya está registrado en la base de datos.', 'error')
        return redirect(url_for('registro'))
    # -----------------------------------------

    # --- 2. AGREGAR (Si la validación fue exitosa) ---
    try:
        if person_type == 'NATURAL':
            agregar_cliente(person_type, comun_data, especifica_data)
            flash(f'✅ Persona Natural {full_name} agregada con éxito.')
        
        elif person_type == 'LEGAL':
            agregar_cliente(person_type, comun_data, especifica_data)
            flash(f'✅ Empresa {company_name} agregada con éxito.')
            
    except Exception as e:
        flash(f'❌ Error al agregar cliente: {e}', 'error')
        
    return redirect(url_for('index'))


# ----------------------------------------------------------------------
# 3. Rutas de Edición (UPDATE)
# ----------------------------------------------------------------------

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    
    cliente = obtener_cliente(id) 
    
    if not cliente:
        flash("Cliente no encontrado.", "error")
        return redirect(url_for('index'))

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
            
        return redirect(url_for('index'))

    # Método GET: Muestra el formulario con los datos cargados
    return render_template('editar.html', cliente=cliente, active_page='listar')


# ----------------------------------------------------------------------
# 4. Ruta de Vista de Detalle (READ - ONE DETAIL)
# ----------------------------------------------------------------------

@app.route('/ver/<int:id>')
def ver_cliente(id):
    """Muestra todos los campos detallados de un cliente específico."""
    cliente = obtener_cliente(id) 
    
    if not cliente:
        flash("Cliente no encontrado.", "error")
        return redirect(url_for('index'))
        
    # Redirige a la nueva plantilla que muestra todos los campos
    return render_template('ver_cliente.html', cliente=cliente, active_page='listar')


# ----------------------------------------------------------------------
# 5. Rutas de Eliminación (DELETE)
# ----------------------------------------------------------------------

@app.route('/eliminar/<int:id>')
def eliminar(id):
    try:
        eliminar_cliente(id)
        flash(f'✅ Cliente con ID {id} eliminado con éxito.')
    except Exception as e:
        flash(f'❌ Error al intentar eliminar el cliente {id}: {e}', 'error')
    
    return redirect(url_for('index'))

# --- nueva ruta para enviar correo ---
@app.route('/enviar_correo')
def enviar_correo():
    return render_template('enviar_correo.html')

if __name__ == "__main__":
    app.run(debug=True)





