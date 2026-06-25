# MediVerse Hub — Unified Project

This folder combines everything into one runnable app:

```
mediverse_hub/
├── app.py                 # Standalone FastAPI backend (recommended way to run)
├── launch.ipynb           # Same backend, runnable from Jupyter (auto-frees port 8000)
├── requirements.txt
├── insert_sample_data.py  # Optional: seeds bills.db with demo records
├── .env.example           # Copy to .env and fill in your Gemini key
└── static/
    ├── index.html         # Sidebar nav: Dashboard / MedReceipt OCR / SymBot Checker / MediBot Chat
    ├── script.js
    └── style.css
```

## Expected folder layout on your machine

`app.py` and `launch.ipynb` both look for sibling project folders **one level up**:

```
mediverse/
├── hub/                          <-- this folder (app.py, launch.ipynb, static/)
├── Recipt_reader/FinanceFlow-AI/bills.db
├── medicine_assistant/
│   ├── data/jaipur_medical_stores_ml.xlsx
│   └── vectorstore/
└── symptom_checker/
    ├── symbot_transformer.pt
    └── vectorstore/
```

If your real project already has these folders next to `hub/`, just drop this `hub/` folder in place (or merge its contents into your existing `hub/`).

## Setup

```bash
cd mediverse/hub
pip install -r requirements.txt
cp .env.example .env
# edit .env -> set GEMINI_API_KEY (or set LLM_PROVIDER=ollama to skip Gemini entirely)
```

(Optional) seed some demo receipts so the Dashboard isn't empty on first run:
```bash
python insert_sample_data.py
```

## Run — pick ONE

**Option A — plain Python (recommended, simplest):**
```bash
python app.py
```

**Option B — Jupyter:**
Open `launch.ipynb` and run all cells. The last cell auto-detects and kills any
orphaned process still holding port 8000 before starting (this is the fix for
the `winerror 10048` crash from earlier).

Then open **http://127.0.0.1:8000** in your browser.

## What lives where

| Feature | Backend route | Frontend tab |
|---|---|---|
| Dashboard analytics | `GET /api/analytics`, `GET /api/receipts` | Dashboard |
| Receipt/prescription OCR | `POST /api/scan`, `POST /api/receipts` | MedReceipt OCR |
| Symptom checker (PyTorch transformer + RAG) | `POST /api/symptoms` | SymBot Checker |
| Medicine Q&A + nearby pharmacies | `POST /api/medicine` | MediBot Chat |

Ollama (for SymBot explanations and MediBot answers) must be running locally
on `http://localhost:11434` with the `mistral` model pulled:
```bash
ollama pull mistral
ollama serve
```

## Notes on what I checked

- `static/index.html` + `script.js` + `style.css` (your real Antigravity-built
  frontend) — sidebar nav logic is correct (`data-tab` → `{tab}-pane`, with
  matching `.tab-pane.active { display: block }` CSS), all `fetch()` calls use
  relative same-origin paths. I discarded the placeholder dashboard I built
  earlier in this conversation in favor of this real one.
- `app.py` and `launch.ipynb` implement the identical backend — use whichever
  launch method you prefer, not both at once (they'd fight over port 8000).
- `launch.ipynb` here is the already-patched version with the auto port-clear
  fix from earlier in this conversation.
