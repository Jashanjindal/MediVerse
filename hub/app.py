import os
import json
import sqlite3
import base64
import io
import requests
import cv2
import numpy as np
import pandas as pd
from typing import Optional, List
from difflib import get_close_matches

import torch
import torch.nn as nn
import torch.nn.functional as F

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
from dotenv import load_dotenv
from geopy.distance import geodesic

# Load environment variables
load_dotenv()

# Define directories relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "Recipt_reader", "FinanceFlow-AI", "bills.db"))
STORES_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "medicine_assistant", "data", "jaipur_medical_stores_ml.xlsx"))
CHECKPOINT_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "symptom_checker", "symbot_transformer.pt"))

MEDICINE_DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "medicine_assistant", "vectorstore"))
SYMPTOMS_DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "symptom_checker", "vectorstore"))

# --- Database Initialization ---
def init_sqlite_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
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

init_sqlite_db()

# --- PyTorch SymBotTransformer Model Re-declaration ---
class SymptomTokenEmbedding(nn.Module):
    def __init__(self, num_symptoms, d_model):
        super().__init__()
        self.token_embed = nn.Embedding(num_symptoms, d_model)
        self.present_embed = nn.Parameter(torch.randn(d_model) * 0.02)
        self.absent_embed  = nn.Parameter(torch.randn(d_model) * 0.02)
        self.num_symptoms = num_symptoms
        self.d_model = d_model

    def forward(self, x):
        batch_size = x.shape[0]
        idx = torch.arange(self.num_symptoms, device=x.device).unsqueeze(0).expand(batch_size, -1)
        base = self.token_embed(idx)
        presence = x.unsqueeze(-1)
        tokens = base + presence * self.present_embed + (1 - presence) * self.absent_embed
        return tokens

class TransformerEncoderBlock(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()
        self.attn = nn.MultiheadAttention(d_model, num_heads, dropout=dropout, batch_first=True)
        self.norm1 = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Linear(d_ff, d_model),
        )
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        attn_out, attn_weights = self.attn(x, x, x)
        x = self.norm1(x + self.dropout(attn_out))
        ffn_out = self.ffn(x)
        x = self.norm2(x + self.dropout(ffn_out))
        return x, attn_weights

class SymBotTransformer(nn.Module):
    def __init__(self, num_symptoms, num_classes, d_model=64, num_heads=4, d_ff=128, num_layers=2, dropout=0.1):
        super().__init__()
        self.tokenizer = SymptomTokenEmbedding(num_symptoms, d_model)
        self.encoders = nn.ModuleList([
            TransformerEncoderBlock(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])
        self.pool_proj = nn.Linear(d_model, d_model)
        self.classifier = nn.Sequential(
            nn.Linear(d_model, d_model), nn.GELU(), nn.Dropout(dropout), nn.Linear(d_model, num_classes)
        )
        self.severity_head = nn.Sequential(
            nn.Linear(d_model, 32), nn.GELU(), nn.Linear(32, 1)
        )

    def forward(self, x):
        tokens = self.tokenizer(x)
        attn_maps = []
        for encoder in self.encoders:
            tokens, attn_w = encoder(tokens)
            attn_maps.append(attn_w)
        presence = x.unsqueeze(-1)
        weighted = tokens * (presence + 0.1)
        pooled = weighted.sum(dim=1) / (presence.sum(dim=1) + 1e-6)
        pooled = F.gelu(self.pool_proj(pooled))
        disease_logits = self.classifier(pooled)
        severity_pred = self.severity_head(pooled).squeeze(-1)
        return disease_logits, severity_pred, attn_maps

# --- Initialize Models, Databases, and Embeddings ---
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"OK: Device active: {device}")

# Load PyTorch Transformer model
print("INFO: Loading Symptom Classifier Transformer...")
checkpoint = torch.load(CHECKPOINT_PATH, map_location=device, weights_only=False)
ALL_SYMPTOMS = checkpoint['symptom_vocab']
SYMPTOM_TO_IDX = {s: i for i, s in enumerate(ALL_SYMPTOMS)}
NUM_SYMPTOMS = len(ALL_SYMPTOMS)
DISEASE_CLASSES = checkpoint['label_encoder_classes']
NUM_CLASSES = len(DISEASE_CLASSES)

transformer_model = SymBotTransformer(
    num_symptoms=NUM_SYMPTOMS,
    num_classes=NUM_CLASSES,
    d_model=checkpoint['d_model'],
    num_heads=checkpoint['num_heads'],
    d_ff=checkpoint['d_ff'],
    num_layers=checkpoint['num_layers'],
).to(device)
transformer_model.load_state_dict(checkpoint['model_state'])
transformer_model.eval()
print(f"OK: Transformer Classifier loaded: {NUM_SYMPTOMS} symptoms, {NUM_CLASSES} diseases")

# Load Medical Stores data
print("INFO: Loading medical stores catalog...")
try:
    stores_df = pd.read_excel(STORES_PATH)
    stores_df['Latitude'] = pd.to_numeric(stores_df['Latitude'], errors='coerce')
    stores_df['Longitude'] = pd.to_numeric(stores_df['Longitude'], errors='coerce')
    stores_df = stores_df.dropna(subset=['Latitude', 'Longitude'])
    print(f"OK: Medical stores loaded: {len(stores_df)} (Locality count: {stores_df['Locality'].nunique()})")
except Exception as e:
    stores_df = pd.DataFrame()
    print(f"ERROR: Error loading medical stores: {e}")

# Load ChromaDB Vector Stores (Shared Embeddings)
print("INFO: Initializing sentence-transformers embeddings...")
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2', model_kwargs={'device': 'cpu'})

print("INFO: Loading Medicine and Symptoms Vectorstores...")
medicine_vectorstore = Chroma(persist_directory=MEDICINE_DB_PATH, embedding_function=embeddings)
symptoms_vectorstore = Chroma(persist_directory=SYMPTOMS_DB_PATH, embedding_function=embeddings)
print("OK: Vectorstores successfully initialized")

# --- Hinglish Symptom Mapper & Extraction logic ---
HINGLISH_MAP = {
    'bukhaar': 'fever', 'bukhar': 'fever', 'sar dard': 'headache', 'sir dard': 'headache',
    'badan dard': 'muscle pain', 'kamzori': 'fatigue', 'thakaan': 'fatigue',
    'khansi': 'cough', 'jukam': 'continuous sneezing', 'pet dard': 'stomach pain',
    'ulti': 'vomiting', 'matli': 'nausea', 'chakkar': 'dizziness', 'jalan': 'burning micturition',
    'khujli': 'itching', 'daane': 'skin rash', 'saans': 'breathlessness',
}

def extract_symptoms_from_text(text: str, threshold=0.6) -> List[str]:
    text_lower = text.lower()
    for hindi, eng in HINGLISH_MAP.items():
        if hindi in text_lower:
            text_lower = text_lower.replace(hindi, eng)
    
    found = set()
    for symptom in ALL_SYMPTOMS:
        if symptom in text_lower:
            found.add(symptom)
            
    words = text_lower.replace(',', ' ').split()
    for i in range(len(words)):
        for j in range(i+1, min(i+4, len(words)+1)):
            phrase = ' '.join(words[i:j])
            matches = get_close_matches(phrase, ALL_SYMPTOMS, n=1, cutoff=threshold)
            if matches:
                found.add(matches[0])
    return list(found)

# --- Find stores in Jaipur locality ---
def locate_nearest_stores(user_area=None, top_n=3):
    if stores_df.empty or not user_area:
        return []
    
    df = stores_df.copy()
    area_lower = user_area.lower()
    df["score"] = (
        df["Locality"].str.lower().str.contains(area_lower, na=False).astype(int) +
        df["Address"].str.lower().str.contains(area_lower, na=False).astype(int) +
        df["Zone"].str.lower().str.contains(area_lower, na=False).astype(int)
    )
    df = df[df["score"] > 0].sort_values("score", ascending=False)
    
    results = []
    for _, row in df.head(top_n).iterrows():
        phone = str(row.get("Phone Primary", "N/A"))
        if phone.startswith("91") and len(phone) >= 12:
            phone = phone[2:]
        has_delivery = row.get("Has Delivery", False)
        delivery_radius = row.get("Delivery Radius Km", None)
        delivery = (f"Delivery: {delivery_radius}km radius" if pd.notna(delivery_radius) else "Delivery available") if has_delivery else "No delivery"
        timing = "Open 24x7" if row.get("Is 24X7", False) else f"{row.get('Opening Time','N/A')} - {row.get('Closing Time','N/A')}"
        rating = row.get("Google Rating", "N/A")
        reviews = int(row.get("Review Count", 0))
        results.append({
            "name": row['Store Name'],
            "locality": row.get("Locality", "N/A"),
            "rating": f"{rating}/5 ({reviews} reviews)",
            "hours": timing,
            "delivery": delivery,
            "phone": phone,
            "address": row.get("Address", "N/A"),
            "map_link": row.get("Google Maps Link", "N/A")
        })
    return results

# --- Ollama API Helper ---
def call_ollama(prompt: str, url: str, model: str) -> str:
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": 450, "temperature": 0.3}
        }
        res = requests.post(f"{url.rstrip('/')}/api/generate", json=payload, timeout=45)
        res.raise_for_status()
        return res.json().get("response", "").strip()
    except Exception as e:
        return f"Local LLM Error: {str(e)}. Please make sure Ollama is serving on {url} and '{model}' model is pulled."

# --- OpenCV Image Preprocessing ---
def preprocess_img(image_bytes: bytes) -> np.ndarray:
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    max_dim = 1024
    height, width = image.shape[:2]
    if max(height, width) > max_dim:
        scaling_factor = max_dim / float(max(height, width))
        new_size = (int(width * scaling_factor), int(height * scaling_factor))
        image = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
        
    gaussian = cv2.GaussianBlur(image, (0, 0), 2.0)
    unsharp_image = cv2.addWeighted(image, 1.5, gaussian, -0.5, 0)
    return unsharp_image

# --- FastAPI App Server ---
app = FastAPI(title="MediVerse Hub API", version="1.0.0")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files mapping
static_dir = os.path.join(BASE_DIR, "static")
os.makedirs(static_dir, exist_ok=True)

# Pydantic models
class ReceiptSaveRequest(BaseModel):
    patient_name: str
    doctor_or_hospital: str
    date: Optional[str] = None
    total_amount: float
    category: str
    diagnosis_or_symptoms: Optional[str] = None
    medicines_json: str
    raw_text: Optional[str] = None

class SymptomCheckRequest(BaseModel):
    text: str
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"

class MedicineChatRequest(BaseModel):
    question: str
    area: Optional[str] = None
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"

# --- Endpoints ---

@app.get("/")
def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))

# 1. SCAN RECEIPT IMAGE (OCR)
@app.post("/api/scan")
async def scan_receipt(
    file: UploadFile = File(...),
    provider: str = Form("gemini"),
    gemini_key: Optional[str] = Form(None),
    ollama_url: str = Form("http://localhost:11434"),
    ollama_model: str = Form("llama3.2-vision")
):
    try:
        content = await file.read()
        processed_cv = preprocess_img(content)
        
        # Save processed image to memory buffer as JPG
        _, encoded_img = cv2.imencode(".jpg", processed_cv)
        processed_bytes = encoded_img.tobytes()
        
        prompt = """
        You are an expert medical administrative assistant specializing in parsing doctor prescriptions, clinic receipts, pharmacy bills, and lab reports.
        Analyze the provided image and extract the following information in strict JSON format:
        {
            "patient_name": "Name of the patient. If not visible, return 'Unknown'",
            "doctor_or_hospital": "Name of the doctor, hospital, or clinic. If not visible, return 'Unknown'",
            "date": "Date of the consultation, prescription, or receipt (e.g. DD/MM/YYYY). If not visible, return null",
            "total_amount": "Total amount paid or billed as a string (e.g. '120.50' or '1,200.00'). For free prescriptions or if no amount is listed, return '0.00'",
            "category": "Must be one of: Consultation, Pharmacy, Lab Test, Radiology, Other",
            "diagnosis_or_symptoms": "Any listed diagnosis, symptoms, complaints, or indication (e.g., 'Fever and Cough', 'Hypertension', 'Routine Checkup'). If not visible, return null",
            "medicines": [
                {
                    "name": "Name of the medicine or service (e.g., Paracetamol, CBC Test, Consultation Fee)",
                    "dosage": "Dosage instructions, frequency, or quantity (e.g., '500mg, twice a day for 5 days', 'Qty: 2'). If none, return null",
                    "price": "Price of this medicine or service as a string. If not listed, return null"
                }
            ]
        }
        Return ONLY valid JSON. Do not include markdown formatting like ```json.
        """
        
        if provider == "ollama":
            img_base64 = base64.b64encode(processed_bytes).decode("utf-8")
            url = f"{ollama_url.rstrip('/')}/api/chat"
            payload = {
                "model": ollama_model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                        "images": [img_base64]
                    }
                ],
                "stream": False,
                "format": "json"
            }
            response = requests.post(url, json=payload, timeout=65)
            response.raise_for_status()
            text = response.json().get("message", {}).get("content", "").strip()
        else:  # Gemini default
            # Reload env variables to ensure newly saved API key is loaded dynamically
            from dotenv import load_dotenv
            load_dotenv(override=True)
            
            # Find key
            api_key = gemini_key or os.getenv("GEMINI_API_KEY")
            if not api_key or api_key == "your_api_key_here":
                return JSONResponse(status_code=400, content={"error": "Google Gemini API Key not configured. Provide it in .env or the Sidebar."})
            
            from google import genai
            from google.genai import errors
            import time
            
            client = genai.Client(api_key=api_key)
            pil_img = Image.open(io.BytesIO(processed_bytes))
            
            models_to_try = ['gemini-2.5-flash', 'gemini-1.5-flash']
            response = None
            last_error = None
            
            for model_name in models_to_try:
                for attempt in range(3):  # up to 3 attempts with backoff
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=[prompt, pil_img]
                        )
                        break  # success!
                    except errors.APIError as e:
                        last_error = e
                        if e.code == 503 or "503" in str(e) or "UNAVAILABLE" in str(e):
                            time.sleep(1 + attempt * 1.5)
                            continue
                        elif e.code == 429:
                            time.sleep(2 + attempt * 2)
                            continue
                        else:
                            break
                    except Exception as e:
                        last_error = e
                        break
                if response:
                    break
                    
            if not response:
                raise Exception(f"Gemini API request failed: {str(last_error)}")
                
            text = response.text.strip()
            
        # Strip markdown tags if any
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text_clean = text.strip()
        
        parsed_data = json.loads(text_clean)
        
        # Convert processed image to base64 for preview
        b64_processed = base64.b64encode(processed_bytes).decode("utf-8")
        parsed_data["processed_image_b64"] = f"data:image/jpeg;base64,{b64_processed}"
        return parsed_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image scan failed: {str(e)}")

# 2. SAVE EXTRACTED RECEIPT RECORD
@app.post("/api/receipts")
def save_receipt(req: ReceiptSaveRequest):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO medical_receipts (patient_name, doctor_or_hospital, date, total_amount, category, diagnosis_or_symptoms, medicines_json, raw_text)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            req.patient_name or "Unknown",
            req.doctor_or_hospital or "Unknown",
            req.date,
            req.total_amount,
            req.category or "Other",
            req.diagnosis_or_symptoms or "N/A",
            req.medicines_json,
            req.raw_text or "{}"
        ))
        conn.commit()
        conn.close()
        return {"success": True, "message": "Receipt record persisted to SQLite successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database insert error: {str(e)}")

# 3. GET LIST OF ALL SAVED RECEIPTS
@app.get("/api/receipts")
def get_receipts():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM medical_receipts ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database fetch error: {str(e)}")

# 3b. DELETE A SINGLE RECEIPT
@app.delete("/api/receipts/{receipt_id}")
def delete_receipt(receipt_id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM medical_receipts WHERE id = ?", (receipt_id,))
        conn.commit()
        conn.close()
        return {"success": True, "message": f"Receipt record {receipt_id} deleted successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database delete error: {str(e)}")

# 3c. DELETE ALL RECEIPTS
@app.delete("/api/receipts")
def delete_all_receipts():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM medical_receipts")
        conn.commit()
        conn.close()
        return {"success": True, "message": "All receipt records deleted successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database clear error: {str(e)}")

# 4. GET ANALYTICS DATA FOR CHART WIDGETS
@app.get("/api/analytics")
def get_analytics():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM medical_receipts", conn)
        conn.close()
        
        if df.empty:
            return {
                "metrics": {"total_spent": 0, "total_visits": 0, "patients_count": 0},
                "category_data": [], "patient_data": [], "monthly_data": [], "doctor_data": []
            }
            
        df['total_amount'] = pd.to_numeric(df['total_amount'], errors='coerce').fillna(0.0)
        df['parsed_date'] = pd.to_datetime(df['date'], errors='coerce', dayfirst=True)
        
        metrics = {
            "total_spent": float(df['total_amount'].sum()),
            "total_visits": int(len(df)),
            "patients_count": int(df['patient_name'].nunique())
        }
        
        # Category breakdowns
        cat_df = df.groupby('category')['total_amount'].sum().reset_index()
        category_data = cat_df.to_dict(orient="records")
        
        # Patient cost comparison
        pat_df = df.groupby('patient_name')['total_amount'].sum().reset_index()
        patient_data = pat_df.to_dict(orient="records")
        
        # Monthly spent aggregation
        time_df = df.dropna(subset=['parsed_date']).copy()
        if not time_df.empty:
            time_df['YearMonth'] = time_df['parsed_date'].dt.strftime('%Y-%m')
            month_df = time_df.groupby('YearMonth')['total_amount'].sum().reset_index().sort_values('YearMonth')
            monthly_data = month_df.to_dict(orient="records")
        else:
            monthly_data = []
            
        # Top Doctors/Hospitals
        doc_df = df.groupby('doctor_or_hospital')['total_amount'].sum().reset_index()
        doc_df = doc_df.sort_values(by='total_amount', ascending=False).head(5)
        doctor_data = doc_df.to_dict(orient="records")
        
        return {
            "metrics": metrics,
            "category_data": category_data,
            "patient_data": patient_data,
            "monthly_data": monthly_data,
            "doctor_data": doctor_data
        }
    except Exception as e:
        print(f"Error computing analytics: {e}")
        return {
            "metrics": {"total_spent": 0, "total_visits": 0, "patients_count": 0},
            "category_data": [], "patient_data": [], "monthly_data": [], "doctor_data": []
        }

# 5. DIAGNOSE SYMPTOMS (SymBot Pipeline)
@app.post("/api/symptoms")
def diagnose_symptoms(req: SymptomCheckRequest):
    if not req.text.strip():
        return {"error": "Symptoms textbox is empty."}
        
    matched = extract_symptoms_from_text(req.text)
    if not matched:
        return {
            "symptoms": [],
            "error": "Couldn't identify standard symptoms. Try words like: fever, headache, skin rash, stomach pain, vomiting."
        }
        
    # Prepare PyTorch input vector
    vec = np.zeros(NUM_SYMPTOMS, dtype=np.float32)
    for s in matched:
        if s in SYMPTOM_TO_IDX:
            vec[SYMPTOM_TO_IDX[s]] = 1.0
            
    x = torch.tensor(vec, dtype=torch.float32).unsqueeze(0).to(device)
    with torch.no_grad():
        logits, severity_pred, _ = transformer_model(x)
        probs = F.softmax(logits, dim=1).squeeze(0)
        top_probs, top_idx = probs.topk(3)
        
    predictions = []
    for p, idx in zip(top_probs.cpu().numpy(), top_idx.cpu().numpy()):
        predictions.append({
            "disease": DISEASE_CLASSES[idx],
            "probability": float(p)
        })
    severity = round(float(severity_pred.item()), 2)
    
    # Similarity searches (RAG context)
    contexts = []
    seen_diseases = set()
    for pred in predictions:
        docs = symptoms_vectorstore.similarity_search(pred["disease"], k=1)
        if docs:
            contexts.append(docs[0].page_content)
            seen_diseases.add(docs[0].metadata.get("disease", pred["disease"]))
        else:
            contexts.append(f"Disease: {pred['disease']}\\nNo verified database description available.")
            seen_diseases.add(pred["disease"])
            
    symptom_query = ', '.join(matched)
    symptom_docs = symptoms_vectorstore.similarity_search(symptom_query, k=2)
    for doc in symptom_docs:
        d_name = doc.metadata.get("disease", "")
        if d_name not in seen_diseases:
            contexts.append(doc.page_content)
            seen_diseases.add(d_name)
            
    combined_contexts = "\n\n---\n\n".join(contexts)
    pred_summary = '\n'.join([f"  {i+1}. {p['disease']} ({p['probability']*100:.1f}% confidence)" for i, p in enumerate(predictions)])
    
    # Validator Prompt
    prompt = f"""You are SymBot, a knowledgeable AI medical symptom assistant for Indian patients.

A custom Transformer model analyzed the patient's symptoms and predicted these top 3 candidate conditions:
{pred_summary}

Predicted severity score: {severity} / 7

Verified local database entries for candidate conditions and symptom-matched conditions:
{combined_contexts}

Patient self-description: "{req.text}"
Detected symptoms: {', '.join(matched)}

YOUR ROLE:
1. Act as a Clinical Validator. Review the patient's description and detected symptoms against the verified local database entries and your own offline medical knowledge.
2. Determine which condition is the most clinically accurate match.
   - If the Transformer's top prediction is incorrect or doesn't fit the symptoms, explain why and highlight the best match from the database entries.
   - Explain the reasoning clearly based on the matching symptoms.
3. Keep the tone warm, empathetic, simple, and professional.
4. Provide a disclaimer stating you are an AI, not a replacement for a doctor.
5. Provide clear precautions based on the verified local database entry of the most likely disease.
6. If the severity score is above 4.0, strongly advise seeing a medical professional soon.

Response:"""

    explanation = call_ollama(prompt, req.ollama_url, req.ollama_model)
    return {
        "symptoms": matched,
        "predictions": predictions,
        "severity": severity,
        "explanation": explanation
    }

# 6. DISPENSE MEDICINE & SEARCH PHARMACIES (MediBot Pipeline)
@app.post("/api/medicine")
def get_medicine_info(req: MedicineChatRequest):
    if not req.question.strip():
        return {"error": "Question is empty."}
        
    # Search Chroma DB for medicine facts
    docs = medicine_vectorstore.similarity_search(req.question, k=4)
    context = "\n\n".join([d.page_content[:200] for d in docs])
    
    # Store search
    stores = locate_nearest_stores(req.area, top_n=3)
    
    store_section = ""
    if req.area and req.area.strip():
        if stores:
            store_section = f"\n\nNEARBY STORES IN {req.area.upper()}:\n" + "\n\n".join([
                f"- {s['name']} ({s['locality']})\n  Rating: {s['rating']}\n  Hours: {s['hours']}\n  {s['delivery']}\n  Phone: {s['phone']}\n  Address: {s['address']}\n  Maps: {s['map_link']}"
                for s in stores
            ])
        else:
            store_section = f"\n\nNo pharmacy stores matched area '{req.area}' in our Jaipur stores list."
            
    prompt = f"""You are MediBot Jaipur. Answer concisely about Indian medicines.
List medicine names, prices, compositions. Mention nearby stores.
Always remind to consult a doctor. Be brief and clear.

MEDICINE CONTEXT:
{context}
{store_section}

Question: {req.question}
Area: {req.area or 'Not specified'}

Answer:"""

    answer = call_ollama(prompt, req.ollama_url, req.ollama_model)
    return {
        "answer": answer,
        "stores": stores
    }

# Mount static folder
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
