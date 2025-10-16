from flask import Flask, render_template, request, redirect, flash
from funciones_crud import agregar_cliente, listar_clientes, obtener_cliente, actualizar_cliente, eliminar_cliente, buscar_clientes

app = Flask(__name__)
app.secret_key = "mi_clave_secreta"  # Necesario para flash

# Ruta principal: mostrar todos los clientes
@app.route('/')
def index():
    clientes = listar_clientes()
    return render_template("index.html", clientes=clientes, tab_activa="agregar")

# Agregar cliente
@app.route('/agregar', methods=['POST'])
def agregar():
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    email = request.form['email']
    dirección = request.form['dirección']
    teléfono = request.form['teléfono']

    agregar_cliente(nombre, apellido, email, dirección, teléfono)
    flash(f'Cliente {nombre} {apellido} agregado con éxito')
    return redirect('/')

# Editar cliente
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    cliente = obtener_cliente(id)
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        dirección = request.form['dirección']
        teléfono = request.form['teléfono']

        actualizar_cliente(id, nombre, apellido, email, dirección, teléfono)
        flash(f'Cliente {nombre} {apellido} actualizado con éxito')
        return redirect('/')
    return render_template('editar.html', cliente=cliente)

# Eliminar cliente
@app.route('/eliminar/<int:id>')
def eliminar(id):
    cliente = obtener_cliente(id)
    eliminar_cliente(id)
    flash(f'Cliente {cliente["nombre"]} {cliente["apellido"]} eliminado con éxito')
    return redirect('/')

# Buscar clientes
@app.route('/buscar', methods=['GET'])
def buscar():
    filtro = request.args.get('filtro', '')
    if filtro:
        clientes = buscar_clientes(filtro)
    else:
        clientes = listar_clientes()
    return render_template('index.html', clientes=clientes, filtro=filtro, tab_activa="buscar")

if __name__ == "__main__":
    app.run(debug=True)







