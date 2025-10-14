import mysql.connector

def conexion_mysql():
 conexion= mysql.connector.connect(
     user="root",
     password="",
     host="localhost",
     database="Clientes" )
 return conexion

