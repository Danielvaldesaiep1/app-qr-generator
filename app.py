from flask import Flask, render_template, request, jsonify, url_for, redirect, flash, session
import os
import qrcode
import io
import base64
from datetime import datetime
from database import get_qr_by_id , update_qr,get_db_connection
import mysql.connector  # Cambiado para usar MySQL


app = Flask(__name__)
app.secret_key = os.urandom(24)

# app.secret_key = 'tu_clave_secreta_aqui'  # Reemplaza con una clave segura y única

# Función para inicializar la conexión con la base de datos MySQL
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",      # Cambia por la dirección de tu servidor MySQL
        user="root",      # Cambia por tu usuario de MySQL
        password="",  # Cambia por tu contraseña de MySQL
        database="qr_code"   # Cambia por el nombre de tu base de datos
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    data = request.json['data']  # Obtener el dato enviado desde la solicitud
    name = request.json['name']  # Obtener el dato enviado desde la solicitud
    fecha_creacion = datetime.now()
    
    
    # Generar código QR
    qr_img = qrcode.make(data)
    
    # Guardar el QR en memoria
    img_io = io.BytesIO()
    qr_img.save(img_io, 'PNG')
    img_io.seek(0)
    
    # Convertir la imagen a binarios para guardarla en la base de datos
    img_binary = img_io.getvalue()
    
    # Guardar los datos en la base de datos MySQL
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute("INSERT INTO info_codigo (data, image, fecha_creacion,nombre_qr) VALUES (%s, %s, %s, %s)", (data, img_binary, fecha_creacion,name))
        conn.commit()
        qr_id = c.lastrowid  # Obtener el último ID insertado
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({'error': str(err)}), 500
    finally:
        c.close()
        conn.close()
    
    # Convertir la imagen a base64 para enviarla al frontend
    img_base64 = base64.b64encode(img_binary).decode('ascii')
    
    return jsonify({'img': img_base64, 'id': qr_id})



@app.route('/mis_qr')
def mis_qr():
    return personal_qr()

#Ruta para mostrar codigos qr 
@app.route('/personal_qr')
def personal_qr():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT id,nombre_qr, data, fecha_creacion FROM info_codigo ")
        qr_codes = cursor.fetchall()
        return render_template('personal_qr.html', qr_codes=qr_codes)
    except mysql.connector.Error as err:
        return render_template('personal_qr.html', error=str(err))
    finally:
        cursor.close()
        conn.close()




    
@app.route('/update_selected_qr/<int:qr_id>')
def update_selected_qr(qr_id):
    qr = get_qr_by_id(qr_id)
    if qr:
        # Si 'image' no está en qr, establece un valor predeterminado
        if 'image' not in qr:
            qr['image'] = None
        return render_template('update_selected_qr.html', qr=qr)
    else:
        flash('Codigo QR no existe', 'error')
        return redirect(url_for('personal_qr'))

@app.route('/guardar_actualizacion_qr/<int:qr_id>', methods=['POST'])
def guardar_actualizacion_qr(qr_id):
    nombre_qr = request.form['nombre_qr']
    data = request.form['data']
    if update_qr(qr_id, nombre_qr, data):
        flash('Codigo QR actualizado correctamente', 'success')
        return redirect(url_for('personal_qr'))
    else:
        flash('Error al actualizar codigo QR', 'error')
        return redirect(url_for('update_selected_qr', qr_id=qr_id))





    

# Ruta para mostrar el código QR desde la base de datos
@app.route('/qr/<int:id>', methods=['GET'])
def get_qr(id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT image FROM info_codigo WHERE id=%s", (id,))
    qr_image = c.fetchone()
    c.close()
    conn.close()

    if qr_image:
        # Convertir binarios a base64
        img_base64 = base64.b64encode(qr_image[0]).decode('ascii')
        # Mostrar imagen en base64 en el navegador
        return f'<img src="data:image/png;base64,{img_base64}" alt="QR Code">'
    else:
        return "QR Code not found", 404




if __name__ == "__main__":
    app.run(debug=True)