from flask import Flask, render_template, request, jsonify
import qrcode
import io
import base64
import mysql.connector  # Cambiado para usar MySQL

app = Flask(__name__)

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
        c.execute("INSERT INTO info_codigo (data, image) VALUES (%s, %s)", (data, img_binary))
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
