# export_csv.py
import sqlite3
import pandas as pd

def export_to_csv():
    conn = sqlite3.connect("db/attendance.db")  # ✅ correct path!
    df = pd.read_sql_query("SELECT * FROM attendance", conn)
    df.to_csv("attendance.csv", index=False)
    print("✅ Attendance exported to attendance.csv")

export_to_csv()
