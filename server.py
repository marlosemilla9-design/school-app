"""
School Management System — Flask Backend
Serves index.html and provides /api/data + /api/version endpoints.
Data is persisted in a SQLite database at data/school.db.
"""

import json
import os
import sqlite3
import threading
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder="public", static_url_path="")

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "data", "school.db"))
_lock = threading.Lock()


# ── Database helpers ──────────────────────────────────────────────────────────

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS store (
                key   TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS version (
                id      INTEGER PRIMARY KEY CHECK (id = 1),
                version INTEGER NOT NULL DEFAULT 0
            )
        """)
        # Ensure exactly one version row exists
        conn.execute("INSERT OR IGNORE INTO version (id, version) VALUES (1, 0)")
        conn.commit()


def read_data():
    with get_conn() as conn:
        row = conn.execute("SELECT value FROM store WHERE key = 'db'").fetchone()
        ver = conn.execute("SELECT version FROM version WHERE id = 1").fetchone()
    return (json.loads(row["value"]) if row else None), (ver["version"] if ver else 0)


def write_data(data: dict, new_version: int):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO store (key, value) VALUES ('db', ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (json.dumps(data),),
        )
        conn.execute("UPDATE version SET version = ? WHERE id = 1", (new_version,))
        conn.commit()


# ── API routes ────────────────────────────────────────────────────────────────

@app.route("/api/version")
def api_version():
    _, version = read_data()
    return jsonify({"version": version})


@app.route("/api/data", methods=["GET"])
def api_get():
    data, version = read_data()
    return jsonify({"data": data, "version": version})


@app.route("/api/data", methods=["POST"])
def api_post():
    body = request.get_json(force=True)
    incoming_data = body.get("data")
    base_version   = body.get("baseVersion", 0)
    force          = body.get("force", False)

    with _lock:
        current_data, current_version = read_data()

        # Conflict detection: someone else saved since the client last loaded
        if not force and current_version != base_version:
            return jsonify({"data": current_data, "version": current_version}), 409

        new_version = current_version + 1
        write_data(incoming_data, new_version)

    return jsonify({"version": new_version})


# ── Static / SPA fallback ─────────────────────────────────────────────────────

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    # Serve real files from public/ if they exist, otherwise return index.html
    file_path = os.path.join(app.static_folder, path)
    if path and os.path.isfile(file_path):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")


# ── Startup ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
else:
    # Called by gunicorn
    init_db()
