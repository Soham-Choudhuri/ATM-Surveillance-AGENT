import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "incidents.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            type TEXT NOT NULL,
            severity TEXT NOT NULL,
            summary TEXT,
            details TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cameras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL
        )
    ''')
    
    # Seed default camera if table is empty
    cursor.execute('SELECT COUNT(*) FROM cameras')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO cameras (name, url) VALUES (?, ?)', ('Local Webcam', '0'))
    conn.commit()
    conn.close()

def insert_log(log_type: str, severity: str, summary: str, details: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO logs (timestamp, type, severity, summary, details)
        VALUES (?, ?, ?, ?, ?)
    ''', (timestamp, log_type, severity, summary, json.dumps(details) if details else "{}"))
    conn.commit()
    conn.close()

def get_logs(limit=50):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, timestamp as Time, type as Type, severity as Severity, summary as Summary, details as Details
        FROM logs
        ORDER BY id DESC
        LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    logs = []
    for row in rows:
        log = dict(row)
        if log.get('Details'):
            try:
                log['Details'] = json.loads(log['Details'])
            except:
                pass
        logs.append(log)
    return logs

def delete_log(log_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM logs WHERE id = ?', (log_id,))
    conn.commit()
    conn.close()

def clear_all_logs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM logs')
    conn.commit()
    conn.close()

# Camera DB Functions
def get_cameras():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, url FROM cameras ORDER BY id ASC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_camera(name: str, url: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO cameras (name, url) VALUES (?, ?)', (name, url))
    conn.commit()
    conn.close()

def delete_camera(camera_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM cameras WHERE id = ?', (camera_id,))
    conn.commit()
    conn.close()

# Initialize on import
init_db()
