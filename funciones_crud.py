from conexion import conectar

def agregar_cliente(nombre, apellido, email):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO clientes (nombre, apellido, email) VALUES (%s, %s, %s)", (nombre, apellido, email))
    conexion.commit()
    conexion.close()

def listar_clientes():
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clientes")
    resultados = cursor.fetchall()
    conexion.close()
    return resultados

def obtener_cliente(id):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clientes WHERE id = %s", (id,))
    resultado = cursor.fetchone()
    conexion.close()
    return resultado

def actualizar_cliente(id, nombre, apellido, email):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("UPDATE clientes SET nombre=%s, apellido=%s, email=%s WHERE id=%s", (nombre, apellido, email, id))
    conexion.commit()
    conexion.close()

def eliminar_cliente(id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM clientes WHERE id=%s", (id,))
    conexion.commit()
    conexion.close()


