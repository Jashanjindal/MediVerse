# pyrefly: ignore [missing-import]
import os
import json
import base64
import io
import requests
import sqlite3
import numpy as np
import pandas as pd
import cv2
import gradio as gr
from PIL import Image
from dotenv import load_dotenv
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server environments
import matplotlib.pyplot as plt

from utils.preprocessing import preprocess_image
from utils.llm_parser import extract_medical_data
from database import create_table, insert_medical_receipt, get_all_medical_receipts

# Load environment variables
load_dotenv()
create_table()

# Set up matplotlib style for cohesive look
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['text.color'] = '#374151'
plt.rcParams['axes.labelcolor'] = '#374151'
plt.rcParams['xtick.color'] = '#4b5563'
plt.rcParams['ytick.color'] = '#4b5563'

# --- Helper Functions for Ollama Models ---
def fetch_ollama_models(url):
    try:
        response = requests.get(f"{url.rstrip('/')}/api/tags", timeout=2)
        if response.status_code == 200:
            models_data = response.json().get("models", [])
            return [m["name"] for m in models_data]
    except Exception:
        pass
    return []

# --- Matplotlib Plot Generation ---
def create_category_spend_plot(cat_df):
    fig, ax = plt.subplots(figsize=(6, 4.5), dpi=100)
    if cat_df is not None and not cat_df.empty:
        bars = ax.bar(cat_df['category'], cat_df['total_amount'], color='#0f766e', width=0.5, edgecolor='#0d9488', linewidth=0.5)
        ax.set_ylabel("Total Amount (₹)", fontsize=10, fontweight='bold', color='#374151')
        ax.set_xlabel("Category", fontsize=10, fontweight='bold', color='#374151')
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'₹{height:,.0f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8, color='#374151', fontweight='semibold')
    else:
        ax.text(0.5, 0.5, "No data available", ha='center', va='center', color='#9ca3af')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cbd5e1')
    ax.spines['bottom'].set_color('#cbd5e1')
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    plt.tight_layout()
    return fig

def create_patient_spend_plot(pat_df):
    fig, ax = plt.subplots(figsize=(6, 4.5), dpi=100)
    if pat_df is not None and not pat_df.empty:
        bars = ax.bar(pat_df['patient_name'], pat_df['total_amount'], color='#6366f1', width=0.5, edgecolor='#4f46e5', linewidth=0.5)
        ax.set_ylabel("Total Cost (₹)", fontsize=10, fontweight='bold', color='#374151')
        ax.set_xlabel("Patient", fontsize=10, fontweight='bold', color='#374151')
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'₹{height:,.0f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8, color='#374151', fontweight='semibold')
    else:
        ax.text(0.5, 0.5, "No data available", ha='center', va='center', color='#9ca3af')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cbd5e1')
    ax.spines['bottom'].set_color('#cbd5e1')
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    plt.tight_layout()
    return fig

def create_monthly_spend_plot(month_df):
    fig, ax = plt.subplots(figsize=(6, 4.5), dpi=100)
    if month_df is not None and not month_df.empty:
        ax.plot(month_df['YearMonth'], month_df['total_amount'], color='#db2777', marker='o', linewidth=2.5, markersize=7, markerfacecolor='#db2777', markeredgecolor='white', markeredgewidth=1.5)
        ax.set_ylabel("Total Amount (₹)", fontsize=10, fontweight='bold', color='#374151')
        ax.set_xlabel("Month", fontsize=10, fontweight='bold', color='#374151')
        for i, txt in enumerate(month_df['total_amount']):
            ax.annotate(f'₹{txt:,.0f}', (month_df['YearMonth'].iloc[i], month_df['total_amount'].iloc[i]),
                        textcoords="offset points", xytext=(0,10), ha='center', fontsize=8, color='#374151', fontweight='semibold')
    else:
        ax.text(0.5, 0.5, "No data available", ha='center', va='center', color='#9ca3af')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cbd5e1')
    ax.spines['bottom'].set_color('#cbd5e1')
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    plt.tight_layout()
    return fig

def create_doctor_spend_plot(doc_df):
    fig, ax = plt.subplots(figsize=(6, 4.5), dpi=100)
    if doc_df is not None and not doc_df.empty:
        bars = ax.barh(doc_df['doctor_or_hospital'], doc_df['total_amount'], color='#ea580c', height=0.5, edgecolor='#d97706', linewidth=0.5)
        ax.set_xlabel("Total Spend (₹)", fontsize=10, fontweight='bold', color='#374151')
        ax.set_ylabel("Doctor / Hospital", fontsize=10, fontweight='bold', color='#374151')
        for bar in bars:
            width = bar.get_width()
            ax.annotate(f'  ₹{width:,.0f}',
                        xy=(width, bar.get_y() + bar.get_height() / 2),
                        xytext=(3, 0),
                        textcoords="offset points",
                        ha='left', va='center', fontsize=8, color='#374151', fontweight='semibold')
    else:
        ax.text(0.5, 0.5, "No data available", ha='center', va='center', color='#9ca3af')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cbd5e1')
    ax.spines['bottom'].set_color('#cbd5e1')
    ax.grid(axis='x', linestyle='--', alpha=0.3)
    plt.tight_layout()
    return fig

# --- State & Filter Management ---
def load_data_and_update_filters():
    receipts = get_all_medical_receipts()
    if not receipts:
        empty_df = pd.DataFrame(columns=["id", "patient_name", "doctor_or_hospital", "date", "total_amount", "category", "diagnosis_or_symptoms", "medicines_json"])
        return empty_df, ["All"], ["All"], ["All"]
        
    df = pd.DataFrame(receipts)
    df['parsed_date'] = pd.to_datetime(df['date'], errors='coerce')
    df['Month'] = df['parsed_date'].dt.strftime('%b %Y')
    df['Year'] = df['parsed_date'].dt.year
    
    patients = ["All"] + sorted(list(df['patient_name'].dropna().unique()))
    categories = ["All"] + sorted(list(df['category'].dropna().unique()))
    doctors = ["All"] + sorted(list(df['doctor_or_hospital'].dropna().unique()))
    
    return df, patients, categories, doctors

def update_analytics(df, selected_patient, selected_category, selected_doctor):
    if df is None or df.empty:
        empty_html_spent = "<div style='background-color:#f0fdfa; border-left:4px solid #0f766e; padding:15px; border-radius:8px; text-align:center;'><p style='margin:0; font-size:0.85rem; color:#0f766e; font-weight:700; text-transform:uppercase;'>Total Health Spend</p><h3 style='margin:6px 0 0 0; font-size:1.85rem; color:#0f766e; font-weight:800;'>₹ 0.00</h3></div>"
        empty_html_visits = "<div style='background-color:#eef2ff; border-left:4px solid #4f46e5; padding:15px; border-radius:8px; text-align:center;'><p style='margin:0; font-size:0.85rem; color:#4f46e5; font-weight:700; text-transform:uppercase;'>Medical Visits / Bills</p><h3 style='margin:6px 0 0 0; font-size:1.85rem; color:#4f46e5; font-weight:800;'>0</h3></div>"
        empty_html_patients = "<div style='background-color:#fdf2f8; border-left:4px solid #db2777; padding:15px; border-radius:8px; text-align:center;'><p style='margin:0; font-size:0.85rem; color:#db2777; font-weight:700; text-transform:uppercase;'>Patients Count</p><h3 style='margin:6px 0 0 0; font-size:1.85rem; color:#db2777; font-weight:800;'>0</h3></div>"
        return (
            empty_html_spent, empty_html_visits, empty_html_patients,
            None, None, None, None,
            pd.DataFrame(columns=["id", "patient_name", "doctor_or_hospital", "date", "total_amount", "category", "diagnosis_or_symptoms"]),
            gr.update(choices=[], value="")
        )
        
    filtered_df = df.copy()
    if selected_patient != "All":
        filtered_df = filtered_df[filtered_df['patient_name'] == selected_patient]
    if selected_category != "All":
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    if selected_doctor != "All":
        filtered_df = filtered_df[filtered_df['doctor_or_hospital'] == selected_doctor]
        
    total_spent = filtered_df['total_amount'].sum()
    total_visits = len(filtered_df)
    unique_patients = filtered_df['patient_name'].nunique()
    
    # HTML Cards for Metrics
    html_spent = f"""
    <div style="background-color: #f0fdfa; border-left: 4px solid #0f766e; padding: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); text-align: center;">
        <p style="margin: 0; font-size: 0.85rem; color: #0f766e; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">💰 Total Health Spend</p>
        <h3 style="margin: 6px 0 0 0; font-size: 1.85rem; color: #0f766e; font-weight: 800;">₹ {total_spent:,.2f}</h3>
    </div>
    """
    html_visits = f"""
    <div style="background-color: #eef2ff; border-left: 4px solid #4f46e5; padding: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); text-align: center;">
        <p style="margin: 0; font-size: 0.85rem; color: #4f46e5; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">📅 Medical Visits / Bills</p>
        <h3 style="margin: 6px 0 0 0; font-size: 1.85rem; color: #4f46e5; font-weight: 800;">{total_visits}</h3>
    </div>
    """
    html_patients = f"""
    <div style="background-color: #fdf2f8; border-left: 4px solid #db2777; padding: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); text-align: center;">
        <p style="margin: 0; font-size: 0.85rem; color: #db2777; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">👤 Patients Count</p>
        <h3 style="margin: 6px 0 0 0; font-size: 1.85rem; color: #db2777; font-weight: 800;">{unique_patients}</h3>
    </div>
    """
    
    # Aggregations for Charts
    cat_df = filtered_df.groupby('category')['total_amount'].sum().reset_index()
    pat_df = filtered_df.groupby('patient_name')['total_amount'].sum().reset_index()
    
    time_df = filtered_df.dropna(subset=['parsed_date']).copy()
    if not time_df.empty:
        time_df['YearMonth'] = time_df['parsed_date'].dt.to_period('M').astype(str)
        month_df = time_df.groupby('YearMonth')['total_amount'].sum().reset_index()
        month_df = month_df.sort_values(by='YearMonth')
    else:
        month_df = pd.DataFrame(columns=["YearMonth", "total_amount"])
        
    doc_df = filtered_df.groupby('doctor_or_hospital')['total_amount'].sum().reset_index()
    doc_df = doc_df.sort_values(by='total_amount', ascending=False).head(5)
    
    # History logs dataframe
    display_df = filtered_df[['id', 'patient_name', 'doctor_or_hospital', 'date', 'total_amount', 'category', 'diagnosis_or_symptoms']].copy()
    display_df.rename(columns={
        'id': 'ID',
        'patient_name': 'Patient Name',
        'doctor_or_hospital': 'Doctor / Hospital',
        'date': 'Date',
        'total_amount': 'Amount (₹)',
        'category': 'Category',
        'diagnosis_or_symptoms': 'Diagnosis / Symptoms'
    }, inplace=True)
    
    id_list = sorted(filtered_df['id'].tolist(), reverse=True)
    id_choices = [str(i) for i in id_list]
    
    return (
        html_spent, html_visits, html_patients,
        cat_df, pat_df, month_df, doc_df,
        display_df,
        gr.update(choices=id_choices, value=id_choices[0] if id_choices else "")
    )

# --- Event Handlers ---
def check_ollama_and_update_models_helper(url):
    models = fetch_ollama_models(url)
    if models:
        return gr.update(visible=True), gr.update(choices=models, value=models[0], visible=True), "✅ Connected to Ollama server!"
    else:
        return gr.update(visible=True), gr.update(choices=[], value="llama3.2-vision", visible=True), "❌ Could not connect to Ollama. Verify Ollama is running (`ollama serve`) locally."

def handle_provider_change(provider, url):
    if provider == "Online (Google Gemini)":
        gemini_vis = gr.update(visible=True)
        ollama_vis = gr.update(visible=False)
        status_text = ""
        return gemini_vis, ollama_vis, status_text
    else:
        gemini_vis = gr.update(visible=False)
        ollama_vis, model_update, status_text = check_ollama_and_update_models_helper(url)
        return gemini_vis, ollama_vis, status_text

def process_and_extract(image_np, provider, gemini_key, ollama_url, ollama_model):
    if image_np is None:
        return None, "", "", "", "", "Other", "", [["", "", ""]], {"error": "Please upload a receipt/prescription image."}
        
    # Preprocess image
    processed_image = preprocess_image(image_np)
    
    # Configure API Keys/Endpoints
    if provider == "Online (Google Gemini)":
        if gemini_key:
            os.environ["GEMINI_API_KEY"] = gemini_key
        prov_name = "gemini"
    else:
        prov_name = "ollama"
        
    extracted_data = extract_medical_data(
        processed_image,
        provider=prov_name,
        ollama_model=ollama_model,
        ollama_url=ollama_url
    )
    
    if "error" in extracted_data:
        return (
            processed_image,
            "Error",
            "Error",
            "",
            "0.00",
            "Other",
            extracted_data["error"],
            [["", "", ""]],
            extracted_data
        )
        
    patient_name = extracted_data.get("patient_name", "Unknown")
    doctor = extracted_data.get("doctor_or_hospital", "Unknown")
    date = extracted_data.get("date", "")
    total_amount = str(extracted_data.get("total_amount", "0.00"))
    category = extracted_data.get("category", "Other")
    if category not in ["Consultation", "Pharmacy", "Lab Test", "Radiology", "Other"]:
        category = "Other"
    diagnosis = extracted_data.get("diagnosis_or_symptoms", "")
    
    meds_list = extracted_data.get("medicines", [])
    meds_data = []
    for med in meds_list:
        name = med.get("name", "")
        dosage = med.get("dosage", "")
        price = med.get("price", "")
        meds_data.append([name, dosage, price])
        
    if not meds_data:
        meds_data = [["", "", ""]]
        
    return (
        processed_image,
        patient_name,
        doctor,
        date,
        total_amount,
        category,
        diagnosis,
        meds_data,
        extracted_data
    )

def save_extracted_record(patient_name, doctor, date, total_amount, category, diagnosis, meds_df, raw_json):
    raw_amount = str(total_amount)
    clean_amount = "".join(c for c in raw_amount if c.isdigit() or c == '.')
    try:
        amt = float(clean_amount) if clean_amount else 0.0
    except ValueError:
        amt = 0.0
        
    meds_list = []
    if meds_df is not None:
        if isinstance(meds_df, pd.DataFrame):
            meds_rows = meds_df.values.tolist()
        else:
            meds_rows = meds_df
            
        for row in meds_rows:
            if len(row) >= 3 and row[0]:  # At least must have a medicine/service name
                name, dosage, price = row[0], row[1], row[2]
                meds_list.append({
                    "name": name,
                    "dosage": dosage if dosage else None,
                    "price": price if price else None
                })
                    
    meds_json_str = json.dumps(meds_list)
    
    try:
        insert_medical_receipt(
            patient_name=patient_name if patient_name else "Unknown",
            doctor_or_hospital=doctor if doctor else "Unknown",
            date=date if date else "Unknown",
            total_amount=amt,
            category=category if category else "Other",
            diagnosis_or_symptoms=diagnosis if diagnosis else "N/A",
            medicines_json=meds_json_str,
            raw_text=json.dumps(raw_json) if raw_json else "{}"
        )
        return "✅ Record saved successfully! Go to the Health Analytics Dashboard tab to see it."
    except Exception as e:
        return f"❌ Database Error: {str(e)}"

def clear_all_records():
    try:
        from database import create_connection
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM medical_receipts")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error clearing records: {e}")
    return refresh_dashboard_data()

def refresh_dashboard_data():
    df, patients, categories, doctors = load_data_and_update_filters()
    html_spent, html_visits, html_patients, cat_df, pat_df, month_df, doc_df, display_df, id_update = update_analytics(df, "All", "All", "All")
    
    fig_cat = create_category_spend_plot(cat_df)
    fig_pat = create_patient_spend_plot(pat_df)
    fig_time = create_monthly_spend_plot(month_df)
    fig_doc = create_doctor_spend_plot(doc_df)
    
    return (
        df,
        gr.update(choices=patients, value="All"),
        gr.update(choices=categories, value="All"),
        gr.update(choices=doctors, value="All"),
        html_spent,
        html_visits,
        html_patients,
        fig_cat,
        fig_pat,
        fig_time,
        fig_doc,
        display_df,
        id_update
    )

def on_filter_change(df, patient, category, doctor):
    html_spent, html_visits, html_patients, cat_df, pat_df, month_df, doc_df, display_df, id_update = update_analytics(df, patient, category, doctor)
    
    fig_cat = create_category_spend_plot(cat_df)
    fig_pat = create_patient_spend_plot(pat_df)
    fig_time = create_monthly_spend_plot(month_df)
    fig_doc = create_doctor_spend_plot(doc_df)
    
    return (
        html_spent,
        html_visits,
        html_patients,
        fig_cat,
        fig_pat,
        fig_time,
        fig_doc,
        display_df,
        id_update
    )

def inspect_record(selected_id, df):
    if not selected_id or df is None or df.empty:
        return "Select a record ID above to inspect details.", pd.DataFrame(columns=["Name", "Dosage", "Price"])
        
    try:
        record_id = int(selected_id)
    except ValueError:
        return "Invalid Record ID", pd.DataFrame(columns=["Name", "Dosage", "Price"])
        
    record_df = df[df['id'] == record_id]
    if record_df.empty:
        return "Record not found", pd.DataFrame(columns=["Name", "Dosage", "Price"])
        
    record = record_df.iloc[0]
    
    details_md = f"""
<div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px;">
    <h3 style="margin-top: 0; color: #1e293b;">📋 Record Details (ID: {record_id})</h3>
    <table style="width: 100%; border-collapse: collapse;">
        <tr><td style="padding: 6px 0; font-weight: bold; width: 30%;">👤 Patient:</td><td style="padding: 6px 0;">{record['patient_name']}</td></tr>
        <tr><td style="padding: 6px 0; font-weight: bold;">🩺 Doctor/Hospital:</td><td style="padding: 6px 0;">{record['doctor_or_hospital']}</td></tr>
        <tr><td style="padding: 6px 0; font-weight: bold;">📅 Date:</td><td style="padding: 6px 0;">{record['date']}</td></tr>
        <tr><td style="padding: 6px 0; font-weight: bold;">🏷️ Category:</td><td style="padding: 6px 0;">{record['category']}</td></tr>
        <tr><td style="padding: 6px 0; font-weight: bold;">💰 Total Cost:</td><td style="padding: 6px 0; color: #0f766e; font-weight: bold;">₹ {record['total_amount']:,.2f}</td></tr>
        <tr><td style="padding: 6px 0; font-weight: bold;">📝 Diagnosis/Symptoms:</td><td style="padding: 6px 0;">{record['diagnosis_or_symptoms']}</td></tr>
    </table>
</div>
"""

    meds_json_str = record['medicines_json']
    try:
        meds_list = json.loads(meds_json_str) if meds_json_str else []
    except Exception:
        meds_list = []
        
    meds_rows = []
    for med in meds_list:
        name = med.get("name", "")
        dosage = med.get("dosage", "")
        price = med.get("price", "")
        meds_rows.append([name, dosage, price])
        
    if meds_rows:
        meds_df = pd.DataFrame(meds_rows, columns=["Name", "Dosage", "Price"])
    else:
        meds_df = pd.DataFrame(columns=["Name", "Dosage", "Price"])
        
    return details_md, meds_df

# --- CSS Styling for Premium Interface ---
custom_css = """
body {
    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background-color: #f8fafc;
}
.gradio-container {
    max-width: 1280px !important;
    margin: 30px auto !important;
    border-radius: 16px;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -4px rgba(0, 0, 0, 0.05);
    background: #ffffff !important;
    border: 1px solid #e2e8f0;
}
.primary-btn {
    background-color: #0f766e !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    box-shadow: 0 2px 4px rgba(15, 118, 110, 0.2);
    transition: all 0.2s ease-in-out !important;
}
.primary-btn:hover {
    background-color: #0d9488 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(13, 148, 136, 0.3);
}
.secondary-btn {
    background-color: #4f46e5 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    box-shadow: 0 2px 4px rgba(79, 70, 229, 0.2);
    transition: all 0.2s ease-in-out !important;
}
.secondary-btn:hover {
    background-color: #6366f1 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(99, 102, 241, 0.3);
}
.danger-btn {
    background-color: #ef4444 !important;
    color: white !important;
    font-weight: bold !important;
}
.sidebar-panel {
    background-color: #f1f5f9;
    border-radius: 12px;
    padding: 15px;
    border: 1px solid #e2e8f0;
}
"""

# --- Build Gradio Interface ---
with gr.Blocks(title="MedReceipt AI Scanner") as demo:
    # State object to store database dataframe
    df_state = gr.State()
    
    gr.HTML("""
        <div style="text-align: center; margin-bottom: 25px; padding-top: 15px;">
            <p style="text-align: center; color: #64748b; font-size: 0.95rem; font-weight: 600; margin-bottom: 15px; letter-spacing: 0.05em;">
                <span style="color: #4f46e5; font-weight: 700;">Step 3 of MediVerse AI</span> | Medical Receipt & Prescription Scanner | Online + Offline
            </p>
            <h1 style="color: #0f766e; font-size: 2.6rem; font-weight: 800; margin-bottom: 6px; letter-spacing: -0.025em; display: flex; align-items: center; justify-content: center; gap: 10px;">
                🏥 MedReceipt-AI
            </h1>
            <p style="color: #475569; font-size: 1.15rem; font-weight: 500; margin-top: 0;">Doctor Prescription Reader & Health Spending Analyzer</p>
            <div style="width: 80px; height: 4px; background: #0f766e; margin: 12px auto; border-radius: 2px;"></div>
        </div>
    """)
    
    with gr.Row():
        # --- Config Sidebar ---
        with gr.Column(scale=1, min_width=300, elem_classes=["sidebar-panel"]):
            gr.Markdown("### ⚙️ AI Configuration")
            provider_dropdown = gr.Dropdown(
                choices=["Online (Google Gemini)", "Offline (Local Ollama)"],
                value="Online (Google Gemini)" if os.getenv("LLM_PROVIDER", "gemini") == "gemini" else "Offline (Local Ollama)",
                label="Select LLM Provider",
                interactive=True
            )
            
            # Gemini Group
            with gr.Group() as gemini_group:
                gemini_key_input = gr.Textbox(
                    label="Gemini API Key",
                    placeholder="Enter API key or loads from .env",
                    type="password",
                    value=os.getenv("GEMINI_API_KEY", "")
                )
                gemini_status = gr.Markdown(
                    "🔑 **Gemini API Key active.**" if os.getenv("GEMINI_API_KEY") else "⚠️ **GEMINI_API_KEY not found in .env.** Enter one to proceed."
                )
            
            # Ollama Group
            with gr.Group(visible=False) as ollama_group:
                ollama_url_input = gr.Textbox(
                    label="Ollama Host URL",
                    value=os.getenv("OLLAMA_URL", "http://localhost:11434")
                )
                ollama_model_dropdown = gr.Dropdown(
                    label="Select Model",
                    choices=[],
                    allow_custom_value=True,
                    value=os.getenv("OLLAMA_MODEL", "llama3.2-vision")
                )
                ollama_status_md = gr.Markdown("")
                connect_btn = gr.Button("🔄 Connect & Refresh Models", size="sm")
                
        # --- Main Panel ---
        with gr.Column(scale=3):
            with gr.Tabs() as tabs:
                
                # --- Tab 1: Image Processing & Extraction ---
                with gr.Tab("📤 Scan Medical Receipt / Prescription"):
                    gr.Markdown("### Upload a prescription, clinic receipt, or lab report to extract insights.")
                    
                    with gr.Row():
                        image_input = gr.Image(label="Upload Image (JPG, PNG, JPEG)", type="numpy")
                        processed_image_output = gr.Image(label="Processed Image (Ready for AI)", type="numpy", interactive=False)
                    
                    extract_btn = gr.Button("🧠 Extract Medical Data", variant="primary", elem_classes=["primary-btn"])
                    
                    gr.Markdown("### 🤖 AI Extracted Medical Information")
                    
                    with gr.Row():
                        patient_output = gr.Textbox(label="👤 Patient Name", interactive=True)
                        doctor_output = gr.Textbox(label="🩺 Doctor / Hospital", interactive=True)
                        date_output = gr.Textbox(label="📅 Date", interactive=True)
                        amount_output = gr.Textbox(label="💰 Total Amount (₹)", interactive=True)
                        
                    with gr.Row():
                        category_output = gr.Dropdown(
                            choices=["Consultation", "Pharmacy", "Lab Test", "Radiology", "Other"],
                            label="🏷️ Category",
                            value="Other",
                            interactive=True
                        )
                        diagnosis_output = gr.Textbox(label="📝 Diagnosis / Symptoms", interactive=True)
                        
                    meds_table_output = gr.Dataframe(
                        headers=["Name", "Dosage", "Price"],
                        datatype=["str", "str", "str"],
                        column_count=(3, "fixed"),
                        label="💊 Prescribed Medicines & Services (Double click cell to edit/add)",
                        interactive=True
                    )
                    
                    with gr.Row():
                        save_btn = gr.Button("💾 Save Record to Database", variant="secondary", elem_classes=["secondary-btn"])
                        save_status_output = gr.Markdown("")
                        
                    with gr.Accordion("📋 View Raw JSON Response", open=False):
                        raw_json_output = gr.JSON(label="Raw JSON")
                        
                # --- Tab 2: Health Analytics Dashboard ---
                with gr.Tab("📊 Health Analytics Dashboard"):
                    with gr.Row():
                        gr.Markdown("### 📈 Health Spending & Family Medical Trends")
                        refresh_db_btn = gr.Button("🔄 Refresh Dashboard Data", size="sm")
                        clear_db_btn = gr.Button("🗑️ Clear All Records", size="sm", variant="stop")
                        
                    with gr.Row():
                        patient_filter = gr.Dropdown(choices=["All"], value="All", label="Filter by Patient", interactive=True)
                        category_filter = gr.Dropdown(choices=["All"], value="All", label="Filter by Category", interactive=True)
                        doctor_filter = gr.Dropdown(choices=["All"], value="All", label="Filter by Doctor/Clinic", interactive=True)
                        
                    gr.Markdown("#### 📁 Spending & Consultation Overview")
                    with gr.Row():
                        total_spent_html = gr.HTML()
                        total_visits_html = gr.HTML()
                        patients_count_html = gr.HTML()
                        
                    gr.Markdown("#### 📊 Spending Breakdowns")
                    with gr.Row():
                        cat_plot = gr.Plot(label="Category-wise Spending")
                        pat_plot = gr.Plot(label="Patient-wise Costs")
                        
                    with gr.Row():
                        time_plot = gr.Plot(label="Monthly Spending Trend")
                        doc_plot = gr.Plot(label="Top Doctors / Hospitals Spend")
                        
                    gr.Markdown("#### 📜 Full Consultation & Receipt History")
                    history_table = gr.Dataframe(interactive=False, label="All SQLite Records")
                    
                    gr.Markdown("#### 🔍 Medical Record Inspector")
                    with gr.Row():
                        inspector_id_dropdown = gr.Dropdown(choices=[], label="Select a Receipt ID to Inspect", interactive=True)
                    
                    with gr.Row():
                        inspector_details = gr.HTML("Select a receipt ID above to load details.")
                        inspector_meds_table = gr.Dataframe(label="Medicines/Services in this Record", interactive=False)

    # --- Wire Events ---
    # Provider Change Toggle
    provider_dropdown.change(
        handle_provider_change,
        inputs=[provider_dropdown, ollama_url_input],
        outputs=[gemini_group, ollama_group, ollama_status_md]
    )
    
    # Connect to Ollama manually
    connect_btn.click(
        check_ollama_and_update_models_helper,
        inputs=[ollama_url_input],
        outputs=[ollama_group, ollama_model_dropdown, ollama_status_md]
    )
    
    # Extract Action
    extract_btn.click(
        process_and_extract,
        inputs=[image_input, provider_dropdown, gemini_key_input, ollama_url_input, ollama_model_dropdown],
        outputs=[processed_image_output, patient_output, doctor_output, date_output, amount_output, category_output, diagnosis_output, meds_table_output, raw_json_output]
    )
    
    # Save Action
    save_btn.click(
        save_extracted_record,
        inputs=[patient_output, doctor_output, date_output, amount_output, category_output, diagnosis_output, meds_table_output, raw_json_output],
        outputs=[save_status_output]
    )
    
    # Filter Interactions
    filter_inputs = [df_state, patient_filter, category_filter, doctor_filter]
    filter_outputs = [total_spent_html, total_visits_html, patients_count_html, cat_plot, pat_plot, time_plot, doc_plot, history_table, inspector_id_dropdown]
    
    patient_filter.change(on_filter_change, inputs=filter_inputs, outputs=filter_outputs[0:8] + [inspector_id_dropdown])
    category_filter.change(on_filter_change, inputs=filter_inputs, outputs=filter_outputs[0:8] + [inspector_id_dropdown])
    doctor_filter.change(on_filter_change, inputs=filter_inputs, outputs=filter_outputs[0:8] + [inspector_id_dropdown])
    
    # Refresh Actions
    refresh_outputs = [df_state, patient_filter, category_filter, doctor_filter, total_spent_html, total_visits_html, patients_count_html, cat_plot, pat_plot, time_plot, doc_plot, history_table, inspector_id_dropdown]
    
    refresh_db_btn.click(refresh_dashboard_data, inputs=[], outputs=refresh_outputs)
    clear_db_btn.click(clear_all_records, inputs=[], outputs=refresh_outputs)
    
    # Inspector Selection
    inspector_id_dropdown.change(
        inspect_record,
        inputs=[inspector_id_dropdown, df_state],
        outputs=[inspector_details, inspector_meds_table]
    )
    
    # Initial Page Load Dashboard Query
    demo.load(refresh_dashboard_data, inputs=[], outputs=refresh_outputs)

if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        theme=gr.themes.Soft(primary_hue="teal", secondary_hue="slate"),
        css=custom_css
    )
