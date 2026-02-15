import sqlite3
import os

DB_FILE = "flight_app.db"

if not os.path.exists(DB_FILE):
    print(f"Database file {DB_FILE} not found. Nothing to migrate.")
    exit(0)

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

try:
    # Check if column exists first to avoid error or handling it in exception
    cursor.execute("PRAGMA table_info(users)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if "results_per_page" in columns:
        print("Column 'results_per_page' already exists.")
    else:
        cursor.execute("ALTER TABLE users ADD COLUMN results_per_page INTEGER DEFAULT 8")
        conn.commit()
        print("Successfully added 'results_per_page' column to 'users' table.")
        
except sqlite3.Error as e:
    print(f"Error migrating database: {e}")
finally:
    conn.close()
