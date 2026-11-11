from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
# CORS permite que el frontend de Netlify se conecte sin bloqueos de seguridad
CORS(app)

# 1. Función auxiliar para conectar a la base de datos
def get_db_connection():
    conn = sqlite3.connect('casilleros.db')
    conn.row_factory = sqlite3.Row 
    return conn

# 2. Inicializamos tu base de datos (con la misma lógica de tu código original)
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tu misma tabla original
    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS casilleros (
            id INT PRIMARY KEY,
            edificio INT,
            en_uso BOOL
        );
    """)
    
    # Generamos los 100 casilleros del Edificio 5 (IDs 5001 al 5100) si no existen
    try:
        for i in range(1, 101):
            cursor.execute("INSERT INTO casilleros (id, edificio, en_uso) VALUES (?, ?, ?)", (5000 + i, 5, False))
        conn.commit()
    except sqlite3.IntegrityError:
        pass # Si ya existen, ignoramos el error
        
    conn.close()

# 3. ENDPOINT PARA LEER: Trae los casilleros y los manda al mapa de React
@app.route('/api/lockers', methods=['GET'])
def get_lockers():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, edificio, en_uso FROM casilleros")
    rows = cursor.fetchall()
    
    # Convertimos los datos de SQLite a formato JSON para la web
    lockers = []
    for row in rows:
        lockers.append({
            "id": row['id'],
            "edificio": row['edificio'],
            "en_uso": bool(row['en_uso'])
        })
        
    conn.close()
    return jsonify(lockers)

# 4. ENDPOINT PARA RESERVAR (Reemplaza la opción "1" de tu menú original)
@app.route('/api/reserve', methods=['POST'])
def reserve_locker():
    data = request.json
    id_res = data.get('id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tu misma lógica de validación
    cursor.execute("SELECT * FROM casilleros WHERE id = ? AND en_uso = 0", (int(id_res),))
    disp = cursor.fetchone()
    
    if disp is None:
        conn.close()
        return jsonify({"status": "error", "message": "Casillero Ocupado o No Existe"}), 400
    else:
        cursor.execute("UPDATE casilleros SET en_uso = 1 WHERE id = ?", (int(id_res),))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Casillero reservado con éxito!"})

if __name__ == '__main__':
    init_db() # Prepara las tablas antes de iniciar
    print("API de e-Lockers corriendo en http://localhost:5000")
    app.run(debug=True, port=5000)