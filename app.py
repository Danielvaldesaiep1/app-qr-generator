from flask import Flask, render_template, request, jsonify
import qrcode
import io
import base64
import sqlite3

app = Flask(__name__)

# Función para inicializar la base de datos y crear la tabla
def init_db():
    conn = sqlite3.connect('qr_code.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS info_codigo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            image BLOB
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    data = request.json['data']  # Obtener el url especificada desde la solicitud
    
    # Generar código QR
    qr_img = qrcode.make(data)
    
    # Guardar el QR en memoria
    img_io = io.BytesIO()
    qr_img.save(img_io, 'PNG')
    img_io.seek(0)
    
    # Convertir la imagen a binarios para guardarla en la base de datos
    img_binary = img_io.getvalue()
    
    # Guardar los datos en la base de datos
    conn = sqlite3.connect('qr_code.db') 
    c = conn.cursor()
    c.execute("INSERT INTO info_codigo (data, image) VALUES (?, ?)", (data, img_binary))
    conn.commit()
    conn.close()
    
    # Convertir la imagen a base64 para enviarla al frontend
    img_base64 = base64.b64encode(img_binary).decode('ascii')
    
    return jsonify({'img': img_base64})

# Ruta para mostrar el código QR desde la base de datos
@app.route('/qr/<int:id>', methods=['GET'])
def get_qr(id):
    conn = sqlite3.connect('qr_code.db')
    c = conn.cursor()
    c.execute("SELECT image FROM info_codigo WHERE id=?", (id,))
    qr_image = c.fetchone()
    conn.close()

    if qr_image:
        # Convertir binarios a base64
        img_base64 = base64.b64encode(qr_image[0]).decode('ascii')
        # Mostrar imagen en base64 en el navegador
        return f'<img src="data:image/png;base64,{img_base64}" alt="QR Code">'
    else:
        return "QR Code not found", 404

if __name__ == "__main__":
    init_db()  # Inicializa la base de datos al iniciar la aplicación
    app.run(debug=True)
