# 🌌 MediVerse — Unified Intelligent Healthcare Command Center

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat-square&logo=python)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Deep Learning](https://img.shields.io/badge/DL-PyTorch-EE4C2C.svg?style=flat-square&logo=pytorch)](https://pytorch.org/)
[![Database](https://img.shields.io/badge/VectorDB-ChromaDB-blue.svg?style=flat-square)](https://www.trychroma.com/)
[![LLM API](https://img.shields.io/badge/LLM-Gemini%20%2F%20Ollama-orange.svg?style=flat-square)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

Welcome to **MediVerse**, a unified healthcare intelligence platform. MediVerse consolidates local neural symptom classification, vector-search retrieval-augmented generation (RAG) for medicine indexing, OCR medical bill scanning, and clinical validation into one cohesive, premium command center web application.

---

## 📂 Repository Structure

The workspace is organized into modular applications, culminating in the unified web hub:

```text
mediverse/
├── hub/                  # 🌟 Unified MediVerse Hub (FastAPI app)
│   ├── app.py            # Main web backend server
│   ├── static/           # HTML5/CSS3 Command Center UI
│   └── requirements.txt  # Core dependencies
├── Recipt_reader/        # 🏥 MedReceipt OCR & Spend Analytics
│   └── FinanceFlow-AI/   # Gradio dashboard, OCR parser, and SQLite database
├── medicine_assistant/   # 💊 MediBot India (RAG Medicine Search & Store Locator)
│   └── data/             # 250K+ Medicine datasets & Jaipur map records
├── symptom_checker/      # 🩺 SymBot Neural Symptom Checker
│   ├── symbot_transformer.pt # Custom trained PyTorch transformer weights
│   └── data/             # Symptom mappings and severity scales
└── PROJECTS_GUIDE.md     # In-depth technical guides for each module
```

---

## 🌟 Core Modules

### 1. 🏥 MedReceipt OCR & Spend Analytics
* **OCR scanner**: Upload prescriptions, invoices, and reports to automatically extract hospital name, doctor details, diagnosis, total cost, and medication tables.
* **Spend Dashboard**: Fully interactive charts (via Chart.js) tracking month-by-month billing, category breakdowns (Pharmacy, Consultation, Labs, etc.), and patient statistics.
* **Interactive Records**: Review, modify, or add items dynamically through an inline database manager.

### 2. 💊 MediBot India (RAG Medicine Desk)
* **Local Search**: Instantly retrieve composition, active prices, manufacturer details, and side effects for over **253,000 Indian medicines**.
* **Jaipur Store Locator**: Input a local area in Jaipur to locate the nearest pharmacies with physical distance, ratings, contact info, and home delivery availability.
* **Offline First**: Queries are processed locally using semantic embeddings and Ollama.

### 3. 🩺 SymBot Diagnostic Lab
* **Neural Classification**: Feed symptoms in natural English or Hinglish (e.g. *"sar dard", "cough"*). A custom **PyTorch Transformer** predicts the top 3 potential conditions and severity.
* **Clinical Doctor Validator**: Retrieves standard medical descriptions and precautions, routing the results through local Mistral/Gemini to write professional clinical notes.

### 4. 🌟 Unified MediVerse Command Center (`hub`)
Rather than running multiple independent terminals, the **Unified Hub** connects all three apps. It provides a beautiful sidebar command dashboard with responsive layouts, ambient glowing status indicators, and glassmorphism design.

---

## ⚙️ Tech Stack & Architecture

| Layer | Technologies Used | Purpose |
| --- | --- | --- |
| **Frontend** | Vanilla HTML5, CSS3 (Modern Glassmorphism Design System), Chart.js | Unified User Dashboard |
| **Web Server** | FastAPI (ASGI), Uvicorn | High-performance backend & JSON API |
| **Deep Learning** | PyTorch (`SymBotTransformer`), NumPy, Pandas | Symptom Classification Neural Network |
| **Vector DB** | ChromaDB (Chroma Vector Store) | Semantic search & RAG retrieval |
| **Embeddings** | SentenceTransformers (`all-MiniLM-L6-v2`) | Medicine Q&A embeddings |
| **AI LLMs** | Google Gemini 2.5 Flash / Ollama (Mistral, Llama 3.2 Vision) | OCR extraction & Clinical Validation |
| **Database** | SQLite3 | Medical receipts and analytics persistence |

---

## 🚀 Quick Start

### 1. Prerequisites
* **Python 3.10+** installed.
* **Ollama** running locally (if using offline models):
  ```bash
  ollama pull mistral
  ollama pull llama3.2-vision
  ```

### 2. Clone and Setup Environment
Clone the repository:
```bash
git clone https://github.com/Jashanjindal/MediVerse.git
cd MediVerse
```

Configure your environment variables by creating a `.env` file in the `hub/` directory:
```env
# Get your API key from Google AI Studio: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# LLM Configuration (Options: gemini, ollama)
LLM_PROVIDER=gemini
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2-vision
```

### 3. Install Dependencies
Install all required libraries:
```bash
pip install -r hub/requirements.txt
```

### 4. Launch the Command Center
Start the FastAPI server:
```bash
python hub/app.py
```
Open your browser and navigate to **`http://127.0.0.1:8000`** to access the MediVerse Hub dashboard.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE details for details.

*Disclaimer: MediVerse is for educational and reference purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment.*
