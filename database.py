import sqlite3

conn = sqlite3.connect(
    "drivers.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS drivers (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT,

    embedding TEXT,

    driving_style TEXT,

    ac_temperature TEXT,

    ambient_mode TEXT,

    seat_position TEXT,

    assistant_voice TEXT,

    created_at TEXT
)
""")

conn.commit()