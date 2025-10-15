import mysql.connector

def conectar():
 conexion= mysql.connector.connect(
     user="root",
     password="",
     host="localhost",
     database="Clientes" )
 return conexion

