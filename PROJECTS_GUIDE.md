# 🌌 MediVerse Repository: Projects Guide & Unified Hub Documentation

Welcome to the **MediVerse** codebase. This repository contains a collection of intelligent healthcare tools powered by local PyTorch deep learning models, vector-search RAG engines, and Gemini/Ollama LLMs.

This document provides a detailed overview of the existing tools in this folder, followed by a guide on how to configure and run the unified **MediVerse Hub** application which integrates all of them.

---

## 📂 Project Directory Structure

```text
mediverse/
├── Recipt_reader/        # MedReceipt OCR & Spend Analytics (Gradio & Streamlit)
├── medicine_assistant/   # MediBot India (RAG Medicine Search & Jaipur Pharmacy Locator)
├── symptom_checker/      # SymBot Transformer Classifier (PyTorch + Ollama Validator)
├── hub/                  # Unified MediVerse Hub Project
│   ├── app.py            # FastAPI Backend Server
│   ├── launch.ipynb      # Jupyter Notebook Launcher
│   ├── requirements.txt  # Python requirements
│   ├── .env              # Environment config settings
│   └── static/           # HTML/CSS/JS frontend files
└── PROJECTS_GUIDE.md     # You are here!
```

---

## 1. 🏥 MedReceipt OCR & Spend Analytics (`Recipt_reader`)

### Overview
MedReceipt is an AI-powered medical bill, prescription, and report scanner. It parses image uploads (scans/photos), extracts structured billing & clinical data, saves the transactions to SQLite, and displays category-wise financial and consultation charts.

### Tech Stack
- **AI Backend:** Gemini 2.5 Flash / local Ollama Vision models (e.g., `llama3.2-vision`)
- **Image Processing:** OpenCV (dynamic resizing + unsharp masking to enhance text contrast)
- **Database:** SQLite (table: `medical_receipts`)
- **Gradio Application:** `Recipt_reader/FinanceFlow-AI/src/app_gradio.py`

### Data Extracted
- Patient Name & Doctor / Hospital
- Consultation Date & Category (Consultation, Pharmacy, Lab Test, Radiology, Other)
- Total amount billed (in INR)
- Diagnosed symptoms/conditions
- Detailed list of medicines (Name, Dosage instructions, Price per item)

---

## 2. 💊 MediBot India: Medicine & Pharmacy Assistant (`medicine_assistant`)

### Overview
MediBot India is a local medical RAG assistant specialized in Indian medicines and patient questions. It runs 100% offline, allowing users to look up details for over 250,000 Indian medicines and find the closest medical stores in Jaipur.

### Tech Stack
- **Database / Embeddings:** ChromaDB storing `all-MiniLM-L6-v2` embeddings of 253,973 medicines and 16,407 medical Q&A pairs (totaling 361K chunks).
- **Nearby Stores:** Matches input areas (e.g. Malviya Nagar, C-Scheme) to medical store records in Jaipur using coordinates via geodesic mapping.
- **LLM Engine:** Mistral 7B (via Ollama).
- **Gradio Application:** `medicine_assistant/launch.ipynb`

### Key Capabilities
- **Medicine Info:** Instantly look up active compositions, prices, manufacturers, and side effects.
- **Store Locator:** Finds the top 3 nearest pharmacies in Jaipur with rating details, hours, contact numbers, and delivery availability.
- **Privacy First:** Chat processing is done entirely locally without sending data to external APIs.

---

## 3. 🩺 SymBot Transformer Symptom Checker (`symptom_checker`)

### Overview
SymBot is a medical diagnostic assistant. It takes free-text description of symptoms, preprocesses it to detect matching symptoms, and routes it through a custom-trained neural network to predict the top 3 candidate diseases and estimate severity.

### Tech Stack
- **Classifier model:** Custom PyTorch Transformer (`SymBotTransformer`) trained on 41 diseases and 132 symptoms with self-attention mechanism.
- **Severity Predictor:** Dual-head regression network outputting a score from 0.0 to 7.0.
- **Clinical Validation RAG:** Uses ChromaDB to fetch verified descriptions & precautions for predicted diseases, then calls local Mistral via Ollama to write validation notes.
- **Gradio Application:** `symptom_checker/launch.ipynb`

### Pipeline
1. **Extraction:** Fuzzy match and Hinglish mapper matches user input text (e.g. "sar dard", "bukhaar") to 132 symptom tokens.
2. **Inference:** The symptom vector is fed to `SymBotTransformer`, outputting disease probabilities and severity.
3. **Retrieval:** Similarity search retrieves precautions, descriptions, and clinical context.
4. **LLM Validation:** Mistral reviews predictions against medical entries to draft the final recommendation.

---

## 4. 🌟 The Unified Project: MediVerse Hub (`hub`)

The **MediVerse Hub** combines all three sub-projects under a single, cohesive, premium application. Instead of launching multiple separate notebook servers, you can run a single command to access the entire medical ecosystem.

### Features
1. **Unified Navigation Command Center:** Sidebar layout allowing fast switching between pages.
2. **Health Spend & Analytics Dashboard:** Elegant metrics cards, fully interactive charts (using Chart.js to show monthly spending, category splits, patient costs, and top consultations), database log logs, and an inspector to inspect individual receipts.
3. **Medical OCR Scan Station:** Upload receipts or drag-and-drop. View preprocessed image preview. Review extracted details, edit them dynamically in an interactive table, and save them directly to the database.
4. **SymBot Diagnostic Lab:** Describe symptoms in Hinglish/English. Instantly view detected symptoms, predicted severity score (displayed with a glowing gauges-meter), top predicted candidate conditions, and clinical doctor validator responses.
5. **MediBot Pharmacy Desk:** Consult about Indian medicines. Choose your Jaipur locality to look up active prices, compositions, and closest offline shops offering home delivery.

### Setup and Running Instructions

1. **Verify Ollama is Running:**
   Ensure Ollama is started locally and you have pulled the required models:
   ```bash
   ollama pull mistral
   ollama pull llama3.2-vision
   ```

2. **Configure Environment Variables:**
   Create a `.env` file in the `hub/` directory:
   ```env
   # API Keys (For online OCR execution)
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # LLM Backend settings
   LLM_PROVIDER=gemini       # Options: gemini, ollama
   OLLAMA_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2-vision
   ```

3. **Install Dependencies:**
   Install python dependencies inside `hub/requirements.txt`:
   ```bash
   pip install -r hub/requirements.txt
   ```

4. **Launch the Application:**
   You can launch the FastAPI server using either the Python script or the Jupyter Notebook:
   
   - **Option A (Python Script):**
     ```bash
     python hub/app.py
     ```
   
   - **Option B (Jupyter Notebook):**
     Open `hub/launch.ipynb` in your Jupyter Notebook environment and run all cells.
   
   Once started, open your browser and navigate to `http://127.0.0.1:8000` to access the MediVerse Command Center!

---

*Disclaimer: MediVerse Hub is for informational and educational purposes only. Always consult a real doctor before taking any medical action.*
