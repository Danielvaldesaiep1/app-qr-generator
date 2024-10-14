import mysql.connector
from mysql.connector import Error
import base64


def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='qr_code',
            user='root',
            password=''
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

def get_qr_by_id(qr_id):
    connection = get_db_connection()
    if connection is None:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT id, nombre_qr, data, fecha_creacion, image FROM info_codigo WHERE id = %s"
        cursor.execute(query, (qr_id,))
        qr = cursor.fetchone()
        if qr and qr['image']:
            qr['image'] = base64.b64encode(qr['image']).decode('utf-8')
        return qr
    except Error as e:
        print(f"Error retrieving QR code: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def update_qr(qr_id, nombre_qr, data):
    connection = get_db_connection()
    if connection is None:
        return False
    
    try:
        cursor = connection.cursor()
        query = "UPDATE info_codigo SET nombre_qr = %s, data = %s WHERE id = %s"
        cursor.execute(query, (nombre_qr, data, qr_id))
        connection.commit()
        return True
    except Error as e:
        print(f"Error actualizar Codigo QR: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def delete_qr(qr_id):
    connection = get_db_connection()
    if connection is None:
        return False
    
    try:
        cursor = connection.cursor()
        # Corregir la consulta SQL eliminando el * y usando la tabla y el id correctos
        query = "DELETE FROM info_codigo WHERE id = %s"
        cursor.execute(query, (qr_id,))  # Asegurarse de pasar qr_id como tupla
        connection.commit()
        return True
    except Exception as e:
        print(f"Error al eliminar el Código QR: {e}")
        connection.rollback()  # Realiza un rollback si hay error
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


