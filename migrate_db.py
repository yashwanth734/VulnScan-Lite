import sqlite3
import os

db_path = "c:/Users/yashwanth/Desktop/myflaskapp/instance/scans.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()
try:
    c.execute("ALTER TABLE scan_result ADD COLUMN passed_checks TEXT")
    conn.commit()
    print("Column passed_checks added successfully.")
except sqlite3.OperationalError as e:
    print(f"OperationalError (might already exist): {e}")
conn.close()
