from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import time

from qr import generate_token, hash_token, generate_qr_data_url

app = Flask(__name__)
CORS(app)

WEB_CLAIM_URL = "http://localhost:3000/locker/claim"

def get_db_connection():
    conn = sqlite3.connect("casilleros.db")
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            locker_id INTEGER NOT NULL,
            token_hash TEXT NOT NULL UNIQUE,
            expires_at INTEGER NOT NULL,
            used_at INTEGER
        );
    """)

    for i in range(1, 101):
        cursor.execute(
            "INSERT OR IGNORE INTO casilleros (id, edificio, en_uso) VALUES (?, ?, ?)",
            (5000 + i, 5, False)
        )

    for i in range(1, 225):
        cursor.execute(
            "INSERT OR IGNORE INTO casilleros (id, edificio, en_uso) VALUES (?, ?, ?)",
            (1000 + i, 1, False)
        )

    conn.commit()
    conn.close()

init_db()

@app.route("/api/lockers", methods=["GET"])
def get_lockers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, edificio, en_uso FROM casilleros")
    rows = cursor.fetchall()

    lockers = []
    for row in rows:
        lockers.append({
            "id": row["id"],
            "edificio": row["edificio"],
            "en_uso": bool(row["en_uso"])
        })

    conn.close()
    return jsonify(lockers)

@app.route("/api/reserve", methods=["POST"])
def reserve_locker():
    data = request.get_json(silent=True) or {}
    locker_id = data.get("id")

    if locker_id is None:
        return jsonify({"status": "error", "message": "Falta id"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM casilleros WHERE id = ? AND en_uso = 0", (int(locker_id),))
    disp = cursor.fetchone()

    if disp is None:
        conn.close()
        return jsonify({"status": "error", "message": "Casillero ocupado o inexistente"}), 400

    token = generate_token()
    token_hash = hash_token(token)
    expires_at = int(time.time()) + (24 * 60 * 60)

    cursor.execute("UPDATE casilleros SET en_uso = 1 WHERE id = ?", (int(locker_id),))
    cursor.execute(
        "INSERT INTO reservas (locker_id, token_hash, expires_at, used_at) VALUES (?, ?, ?, ?)",
        (int(locker_id), token_hash, expires_at, None)
    )
    conn.commit()
    conn.close()

    claim_url = f"{WEB_CLAIM_URL}?token={token}"
    qr_data_url = generate_qr_data_url(claim_url)

    return jsonify({
        "status": "success",
        "message": "Casillero reservado",
        "locker_id": int(locker_id),
        "qr": qr_data_url,
        "claim_url": claim_url,
        "expires_at": expires_at
    })

@app.route("/api/qr/claim", methods=["POST"])
def claim_qr():
    data = request.get_json(silent=True) or {}
    token = data.get("token")

    if not token:
        return jsonify({"status": "error", "message": "Falta token"}), 400

    token_hash = hash_token(token)
    now = int(time.time())

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT r.id, r.locker_id, r.expires_at, r.used_at
        FROM reservas r
        WHERE r.token_hash = ?
    """, (token_hash,))

    reserva = cursor.fetchone()

    if reserva is None:
        conn.close()
        return jsonify({"status": "error", "message": "QR inválido"}), 400

    if reserva["expires_at"] < now:
        conn.close()
        return jsonify({"status": "error", "message": "QR expirado"}), 400

    if reserva["used_at"] is not None:
        conn.close()
        return jsonify({"status": "error", "message": "QR ya usado"}), 400

    cursor.execute("UPDATE reservas SET used_at = ? WHERE id = ?", (now, reserva["id"]))
    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "message": "QR confirmado",
        "locker_id": reserva["locker_id"]
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
