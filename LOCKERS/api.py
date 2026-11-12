from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

def get_db_connection():
    # Establece la conexión con la base de datos local
    conn = sqlite3.connect('casilleros.db')
    conn.row_factory = sqlite3.Row 
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS casilleros (
            id INT PRIMARY KEY,
            edificio INT,
            en_uso BOOL
        );
    """)
    
    # 1. Generar los 100 casilleros del Edificio 5 (id: 5001 al 5100)
    for i in range(1, 101):
        # INSERT OR IGNORE respeta los casilleros que ya existen
        cursor.execute(
            "INSERT OR IGNORE INTO casilleros (id, edificio, en_uso) VALUES (?, ?, ?)", 
            (5000 + i, 5, False)
        )
        
    # 2. Generar los 224 casilleros del Polideportivo (id: 1001 al 1224)
    for i in range(1, 225):
        cursor.execute(
            "INSERT OR IGNORE INTO casilleros (id, edificio, en_uso) VALUES (?, ?, ?)", 
            (1000 + i, 1, False)
        )
        
    conn.commit()
    conn.close()

# Ejecución de la inicialización de la base de datos al arrancar el servidor
init_db()

@app.route('/api/lockers', methods=['GET'])
def get_lockers():
    # Consulta de todos los casilleros registrados
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, edificio, en_uso FROM casilleros")
    rows = cursor.fetchall()
    
    lockers = []
    for row in rows:
        lockers.append({
            "id": row['id'],
            "edificio": row['edificio'],
            "en_uso": bool(row['en_uso'])
        })
        
    conn.close()
    return jsonify(lockers)

@app.route('/api/reserve', methods=['POST'])
def reserve_locker():
    # Procesa la solicitud de reserva de un casillero específico
    data = request.json
    id_res = data.get('id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM casilleros WHERE id = ? AND en_uso = 0", (int(id_res),))
    disp = cursor.fetchone()
    
    if disp is None:
        conn.close()
        return jsonify({"status": "error", "message": "Casillero Ocupado o No Existe"}), 400
    else:
        cursor.execute("UPDATE casilleros SET en_uso = 1 WHERE id = ?", (int(id_res),))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Casillero reservado con éxito"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
