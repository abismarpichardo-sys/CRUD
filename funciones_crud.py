from conexion import conectar

# --- 1. FUNCIÓN AGREGAR CLIENTE (CREATE) ---
def agregar_cliente(tipo, comun_data, especifica_data):
    conexion = conectar()
    cursor = conexion.cursor()
    
    try:
        query_parent = "INSERT INTO PARENT_TABLE (phone, email, city, address, person_type) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query_parent, (*comun_data, tipo))
        
        cursor.execute("SELECT LAST_INSERT_ID()")
        nuevo_id = cursor.fetchone()[0]
        
        if not nuevo_id:
            raise Exception("No se pudo obtener el ID de la nueva fila.")

        if tipo == 'NATURAL':
            query_child = "INSERT INTO NATURAL_PERSON (id, id_card_number, full_name) VALUES (%s, %s, %s)"
            cursor.execute(query_child, (nuevo_id, *especifica_data))
        
        elif tipo == 'LEGAL':
            query_child = "INSERT INTO LEGAL_PERSON (id, ruc, company_name, industry, codigo_ciiu) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query_child, (nuevo_id, *especifica_data))
            
        conexion.commit()
        return nuevo_id

    except Exception as e:
        conexion.rollback()
        print(f"Error al agregar cliente: {e}")
        return None
    
    finally:
        cursor.close()
        conexion.close()


# --- 2. FUNCIÓN LISTAR CLIENTES (READ - ALL) ---
def listar_clientes():
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True) 
    
    query = """
    SELECT 
        P.*, 
        N.id_card_number, N.full_name,
        L.ruc, L.company_name, L.industry, L.codigo_ciiu 
    FROM 
        PARENT_TABLE P
    LEFT JOIN 
        NATURAL_PERSON N ON P.id = N.id
    LEFT JOIN 
        LEGAL_PERSON L ON P.id = L.id;
    """
    cursor.execute(query)
    resultados = cursor.fetchall()
    
    cursor.close()
    conexion.close()
    return resultados

# --- 3. FUNCIÓN OBTENER CLIENTE (READ - ONE) ---
def obtener_cliente(id):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    
    query = """
    SELECT 
        P.*, 
        N.id_card_number, N.full_name,
        L.ruc, L.company_name, L.industry, L.codigo_ciiu  
    FROM 
        PARENT_TABLE P
    LEFT JOIN 
        NATURAL_PERSON N ON P.id = N.id
    LEFT JOIN 
        LEGAL_PERSON L ON P.id = L.id
    WHERE
        P.id = %s;
    """
    cursor.execute(query, (id,))
    resultado = cursor.fetchone()
    
    cursor.close()
    conexion.close()
    return resultado

# --- 4. FUNCIÓN ACTUALIZAR CLIENTE (UPDATE) ---
def actualizar_cliente(id, tipo, comun_data, especifica_data):
    conexion = conectar()
    cursor = conexion.cursor()
    
    try:
        query_parent = """
            UPDATE PARENT_TABLE 
            SET phone=%s, email=%s, city=%s, address=%s 
            WHERE id=%s
        """
        cursor.execute(query_parent, comun_data) 
        
        if tipo == 'NATURAL':
            query_child = """
                UPDATE NATURAL_PERSON 
                SET id_card_number=%s, full_name=%s 
                WHERE id=%s
            """
            cursor.execute(query_child, especifica_data)
        
        elif tipo == 'LEGAL':
            query_child = """
                UPDATE LEGAL_PERSON 
                SET ruc=%s, company_name=%s, industry=%s, codigo_ciiu=%s 
                WHERE id=%s
            """
            cursor.execute(query_child, especifica_data)
            
        conexion.commit()
    
    except Exception as e:
        conexion.rollback()
        print(f"Error al actualizar cliente: {e}")
    
    finally:
        cursor.close()
        conexion.close()

# --- 5. FUNCIÓN ELIMINAR CLIENTE (DELETE) ---
def eliminar_cliente(id):
    conexion = conectar()
    cursor = conexion.cursor()
    
    try:
        cursor.execute("SELECT person_type FROM PARENT_TABLE WHERE id = %s", (id,))
        resultado = cursor.fetchone()
        
        if resultado is None:
            raise Exception(f"Cliente con ID {id} no encontrado en la base de datos.")
            
        person_type = resultado[0] 
        
        if person_type == 'NATURAL':
            cursor.execute("DELETE FROM NATURAL_PERSON WHERE id = %s", (id,))
        elif person_type == 'LEGAL':
            cursor.execute("DELETE FROM LEGAL_PERSON WHERE id = %s", (id,))
            
        cursor.execute("DELETE FROM PARENT_TABLE WHERE id = %s", (id,))
        
        conexion.commit()
        return True
        
    except Exception as e:
        conexion.rollback()
        print(f"Error al eliminar cliente {id}: {e}")
        raise e 

    finally:
        cursor.close()
        conexion.close()

# --- 6. FUNCIÓN BUSCAR CLIENTES (SEARCH) ---
def buscar_clientes(filtro):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    
    query = """
    SELECT 
        P.*, 
        N.id_card_number, N.full_name,
        L.ruc, L.company_name, L.industry, L.codigo_ciiu 
    FROM 
        PARENT_TABLE P
    LEFT JOIN 
        NATURAL_PERSON N ON P.id = N.id
    LEFT JOIN 
        LEGAL_PERSON L ON P.id = L.id
    WHERE 
        CAST(P.id AS CHAR) LIKE %s OR 
        P.email LIKE %s OR 
        P.address LIKE %s OR 
        N.full_name LIKE %s OR 
        L.company_name LIKE %s OR 
        L.ruc LIKE %s OR
        N.id_card_number LIKE %s OR
        L.codigo_ciiu LIKE %s; 
    """
    filtro_param = f"%{filtro}%"
    
    params = (
        filtro_param, filtro_param, filtro_param, filtro_param, filtro_param, 
        filtro_param, filtro_param, filtro_param
    )
    
    cursor.execute(query, params)
    resultados = cursor.fetchall()
    
    cursor.close()
    conexion.close()
    return resultados

# --- 7. FUNCIÓN FILTRAR POR TIPO (NUEVA) ---
def filtrar_clientes_por_tipo(tipo):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    
    query_base = """
    SELECT 
        P.*, 
        N.id_card_number, N.full_name,
        L.ruc, L.company_name, L.industry, L.codigo_ciiu 
    FROM 
        PARENT_TABLE P
    LEFT JOIN 
        NATURAL_PERSON N ON P.id = N.id
    LEFT JOIN 
        LEGAL_PERSON L ON P.id = L.id
    WHERE
        P.person_type = %s;
    """
    
    cursor.execute(query_base, (tipo,))
    resultados = cursor.fetchall()
    
    cursor.close()
    conexion.close()
    return resultados

# --- 8. FUNCIÓN VERIFICAR UNICIDAD DE CÉDULA/RUC ---
def verificar_identificacion_unica(id_card_number=None, ruc=None):
    conexion = conectar()
    cursor = conexion.cursor()
    
    try:
        if id_card_number:
            query_natural = "SELECT COUNT(id) FROM NATURAL_PERSON WHERE id_card_number = %s"
            cursor.execute(query_natural, (id_card_number,))
            if cursor.fetchone()[0] > 0:
                return True

        if ruc:
            query_legal = "SELECT COUNT(id) FROM LEGAL_PERSON WHERE ruc = %s"
            cursor.execute(query_legal, (ruc,))
            if cursor.fetchone()[0] > 0:
                return True
                
        return False
    
    except Exception as e:
        print(f"Error al verificar unicidad: {e}")
        return True 
        
    finally:
        cursor.close()
        conexion.close()















