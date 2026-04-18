import sqlite3

conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    lang TEXT,
    contact TEXT,
    latitude TEXT,
    longitude TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    service TEXT,
    lang TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()


def save_user(data):
    cursor.execute("""
    INSERT INTO users (user_id, lang, contact, latitude, longitude)
    VALUES (?, ?, ?, ?, ?)
    """, (
        data.get("user_id"),
        data.get("lang"),
        data.get("contact"),
        data.get("lat"),
        data.get("lon")
    ))
    conn.commit()


def save_request(user_id, service, lang):
    cursor.execute("""
    INSERT INTO requests (user_id, service, lang)
    VALUES (?, ?, ?)
    """, (user_id, service, lang))
    conn.commit()