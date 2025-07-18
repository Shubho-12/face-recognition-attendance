# create_db.py
import sqlite3
import os

# Ensure the db folder exists
os.makedirs("db", exist_ok=True)

# Connect to the correct path
conn = sqlite3.connect("db/attendance.db")
c = conn.cursor()

# Create attendance table if not exists
c.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        time TEXT NOT NULL
    )
''')

conn.commit()
conn.close()
print("✅ attendance.db and 'attendance' table created successfully.")
