import sqlite3
import json
import os

DB_PATH = r"c:\Users\alpha\OneDrive\Desktop\mediverse\Recipt_reader\FinanceFlow-AI\bills.db"

def insert_samples():
    if not os.path.exists(DB_PATH):
        # Create directory if doesn't exist
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Ensure table exists
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
    
    # Check count
    cursor.execute("SELECT COUNT(*) FROM medical_receipts")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"Table already has {count} records. Skipping mock database insertion.")
        conn.close()
        return

    print("Inserting premium mock clinical analytics records into bills.db...")
    
    samples = [
        (
            "Rohan Sharma",
            "SMS Hospital, Jaipur",
            "12/06/2026",
            1200.00,
            "Consultation",
            "High fever and acute headache",
            json.dumps([
                {"name": "Paracetamol 650mg", "dosage": "twice daily, 5 days", "price": 60.00},
                {"name": "Pantocid 40mg", "dosage": "once daily before breakfast", "price": 120.00},
                {"name": "Cefixime 200mg", "dosage": "twice daily, 5 days", "price": 220.00}
            ]),
            json.dumps({"source": "Mock System OCR Scanner", "notes": "Fever prescription sample"})
        ),
        (
            "Rohan Sharma",
            "Apex Pharmacy, Jaipur",
            "15/06/2026",
            750.50,
            "Pharmacy",
            "Fever Recovery Support",
            json.dumps([
                {"name": "Multivitamin Capsules", "dosage": "once daily at night", "price": 350.00},
                {"name": "Cough Syrup (Ascoril)", "dosage": "10ml three times daily", "price": 150.00},
                {"name": "ORS Sachet Box", "dosage": "as directed", "price": 100.00}
            ]),
            json.dumps({"source": "Mock System OCR Scanner", "notes": "Pharmacy receipt"})
        ),
        (
            "Priya Patel",
            "Fortis Hospital, Jaipur",
            "10/05/2026",
            4500.00,
            "Lab Test",
            "Routine Blood & Lipid Panels",
            json.dumps([
                {"name": "Complete Blood Count (CBC)", "dosage": "N/A", "price": 800.00},
                {"name": "Lipid Profile Panel", "dosage": "N/A", "price": 1200.00},
                {"name": "Thyroid Profile (T3, T4, TSH)", "dosage": "N/A", "price": 1500.00}
            ]),
            json.dumps({"source": "Mock System OCR Scanner", "notes": "Pathology laboratory report"})
        ),
        (
            "Priya Patel",
            "Dr. B. Lal Lab, Jaipur",
            "22/05/2026",
            2800.00,
            "Radiology",
            "Chest Chest Pain Investigation",
            json.dumps([
                {"name": "Chest X-Ray PA View", "dosage": "N/A", "price": 800.00},
                {"name": "Electrocardiogram (ECG)", "dosage": "N/A", "price": 600.00},
                {"name": "Cardiologist Consultation", "dosage": "N/A", "price": 1400.00}
            ]),
            json.dumps({"source": "Mock System OCR Scanner", "notes": "Radiology lab report"})
        ),
        (
            "Amit Verma",
            "Metro Mas Hospital, Jaipur",
            "05/06/2026",
            3200.00,
            "Consultation",
            "Hypertension & Mild Chest Discomfort",
            json.dumps([
                {"name": "Amlodipine 5mg (Amlokind)", "dosage": "once daily in morning", "price": 90.00},
                {"name": "Atorvastatin 10mg (Lipvas)", "dosage": "once daily at night", "price": 210.00},
                {"name": "Aspirin 75mg (Loprin)", "dosage": "once daily after lunch", "price": 50.00}
            ]),
            json.dumps({"source": "Mock System OCR Scanner", "notes": "Cardiology Consultation"})
        ),
        (
            "Amit Verma",
            "Jaipur Dental Clinic",
            "18/06/2026",
            1500.00,
            "Other",
            "Tooth Cavity Filling & scaling",
            json.dumps([
                {"name": "Dental Scaling & Polish", "dosage": "N/A", "price": 1000.00},
                {"name": "Amoxicillin 500mg", "dosage": "three times daily, 3 days", "price": 120.00}
            ]),
            json.dumps({"source": "Mock System OCR Scanner", "notes": "Dental clinic bill"})
        )
    ]
    
    cursor.executemany("""
    INSERT INTO medical_receipts (patient_name, doctor_or_hospital, date, total_amount, category, diagnosis_or_symptoms, medicines_json, raw_text)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, samples)
    
    conn.commit()
    conn.close()
    print("Database pre-populated with beautiful mock medical records successfully!")

if __name__ == "__main__":
    insert_samples()
