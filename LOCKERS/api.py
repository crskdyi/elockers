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
    # Inicializa la base de datos y crea la tabla si no existe
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS casilleros (
            id INT PRIMARY KEY,
            edificio INT,
            en_uso BOOL
        );
    """)
    
    # Generación de los 100 casilleros iniciales para el edificio 5
    try:
        for i in range(1, 101):
            cursor.execute(
                "INSERT INTO casilleros (id, edificio, en_uso) VALUES (?, ?, ?)", 
                (5000 + i, 5, False)
            )
        conn.commit()
    except sqlite3.IntegrityError:
        # Los registros ya existen, se omite la inserción
        pass
        
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
