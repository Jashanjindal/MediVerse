import sqlite3

def create_connection():
    # Adding a timeout helps prevent "database is locked" errors on Windows
    # when multiple Streamlit threads or external programs access the DB.
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.abspath(os.path.join(base_dir, "..", "bills.db"))
    conn = sqlite3.connect(db_path, timeout=15.0)
    return conn

def create_table():
    conn = create_connection()
    cursor = conn.cursor()

    # Create the new medical_receipts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medical_receipts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT,
        doctor_or_hospital TEXT,
        date TEXT,
        total_amount REAL,
        category TEXT,
        diagnosis_or_symptoms TEXT,
        medicines_json TEXT,
        raw_text TEXT
    )
    """)

    conn.commit()
    conn.close()

def insert_medical_receipt(patient_name, doctor_or_hospital, date, total_amount, category, diagnosis_or_symptoms, medicines_json, raw_text):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO medical_receipts (patient_name, doctor_or_hospital, date, total_amount, category, diagnosis_or_symptoms, medicines_json, raw_text)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (patient_name, doctor_or_hospital, date, total_amount, category, diagnosis_or_symptoms, medicines_json, raw_text))

    conn.commit()
    conn.close()

def get_all_medical_receipts():
    conn = create_connection()
    # To return rows as dictionaries for easy pandas conversion
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM medical_receipts ORDER BY id DESC")
    rows = cursor.fetchall()
    
    conn.close()
    
    # Convert sqlite3.Row objects to dictionaries
    return [dict(row) for row in rows]
