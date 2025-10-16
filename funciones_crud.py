from conexion import conectar

def agregar_cliente(nombre, apellido, email, dirección, teléfono):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO clientes (nombre, apellido, email, dirección, teléfono) VALUES (%s, %s, %s, %s, %s)",
        (nombre, apellido, email, dirección, teléfono)
    )
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

def actualizar_cliente(id, nombre, apellido, email, dirección, teléfono):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE clientes SET nombre=%s, apellido=%s, email=%s, dirección=%s, teléfono=%s WHERE id=%s",
        (nombre, apellido, email, dirección, teléfono, id)
    )
    conexion.commit()
    conexion.close()

def eliminar_cliente(id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM clientes WHERE id=%s", (id,))
    conexion.commit()
    conexion.close()

def buscar_clientes(filtro):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    query = "SELECT * FROM clientes WHERE nombre LIKE %s OR apellido LIKE %s OR CAST(id AS CHAR) LIKE %s"
    filtro_str = str(filtro)
    filtro_param = f"%{filtro_str}%"
    cursor.execute(query, (filtro_param, filtro_param, filtro_param))
    resultados = cursor.fetchall()
    conexion.close()
    return resultados




