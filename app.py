from flask import Flask, render_template, request, redirect
from funciones_crud import agregar_cliente, listar_clientes, obtener_cliente, actualizar_cliente, eliminar_cliente

app = Flask(__name__)

@app.route('/')
def index():
    clientes = listar_clientes()
    return render_template("index.html", clientes=clientes)

@app.route('/agregar', methods=['POST'])
def agregar():
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    email = request.form['email']
    agregar_cliente(nombre, apellido, email)
    return redirect('/')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    cliente = obtener_cliente(id)
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        actualizar_cliente(id, nombre, apellido, email)
        return redirect('/')
    return render_template('editar.html', cliente=cliente)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    eliminar_cliente(id)
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)



