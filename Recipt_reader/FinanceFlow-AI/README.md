# 🏥 MedReceipt-AI

An intelligent, end-to-end Medical Receipt and Prescription Reader.

MedReceipt-AI streamlines medical expense tracking and prescription analysis by processing raw document images through an OpenCV computer vision pipeline, extracting structured clinical and billing data using the state-of-the-art **Gemini 2.5 Flash** model, and saving records to a relational SQLite database for real-time dashboard analytics and family medical spend visualization.

---

## ✨ Features

*   **Intelligent Medical OCR**: Uses Google's latest **Gemini 2.5 Flash** LLM to extract structured fields (Patient Name, Doctor/Hospital, Date, Category, Diagnosis, and Medicines/Services list) from unstructured handwriting and messy print.
*   **Offline Mode (Ollama)**: Supports complete offline execution using local vision models via **Ollama** (e.g., `llama3.2-vision` or `llava`) for users who don't want to use API keys or send data to external APIs.
*   **Computer Vision Preprocessing**: Utilizes **OpenCV** to dynamically resize images and apply unsharp masking, boosting text contrast and minimizing token usage/API latency.
*   **Structured Prescriptions**: Automatically extracts medicine names, dosages, and prices, presenting them in clean interactive tables.
*   **Gradio Web App**: A modern, interactive web application supporting image uploads, AI-powered field correction, interactive dataframe editing, and a rich medical dashboard complete with dark mode compatibility and micro-animations.
*   **Interactive Health Dashboard**: Built with **Gradio** (or **Streamlit**). Features category-wise spend analysis, patient-wise cost comparison, consultation timeline trends, and a complete medical history search engine with a record inspector.
*   **Jupyter Notebook Integration**: Includes a step-by-step Jupyter Notebook (`app.ipynb`) detailing the preprocessing, extraction, database persistence pipeline programmatically, and running the Gradio interface inline.

---

## 🛠️ Tech Stack

*   **Frontend / Dashboard**: Gradio (Primary) / Streamlit (Secondary)
*   **AI / Extraction**: Google GenAI SDK (`gemini-2.5-flash`)
*   **Image Processing**: OpenCV (`opencv-python`), NumPy, Pillow
*   **Data Analysis & Plots**: Pandas, Matplotlib
*   **Database**: SQLite
*   **Notebook**: Jupyter Notebook

---

## ⚙️ How to Run Locally

### 1. Install Dependencies
Make sure you have Python installed, then run:
```bash
pip install -r requirements.txt
```

### 2. Configure Your LLM Backend

You can run MedReceipt-AI either **Online (using Google Gemini)** or **Offline (using local Ollama)**.

#### Option A: Online via Google Gemini
1. Get an API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Create a file named `.env` in the `FinanceFlow-AI` folder.
3. Add your key and set the default provider:
   ```env
   LLM_PROVIDER=gemini
   GEMINI_API_KEY=your_api_key_here
   ```

#### Option B: Offline via Local Ollama (No API Keys Required)
1. Download and install [Ollama](https://ollama.com).
2. Open your terminal and pull a vision-capable model (like `llama3.2-vision`):
   ```bash
   ollama pull llama3.2-vision
   ```
3. Create a file named `.env` in the `FinanceFlow-AI` folder.
4. Set up the environment variables:
   ```env
   LLM_PROVIDER=ollama
   OLLAMA_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2-vision
   ```
   *Note: You can also adjust or test connections to local Ollama endpoints directly from the application's sidebar.*

### 3. Run the Application Dashboard

#### Option A: Run the Gradio Web App (Recommended)
Launch the Gradio interface locally:
```bash
python app_gradio.py
```
Open the local URL displayed in the terminal (usually `http://127.0.0.1:7860`).

#### Option B: Run the Streamlit Web App
If you prefer Streamlit, start the Streamlit server:
```bash
streamlit run app.py
```

### 4. Run the Jupyter Notebook Code
Open the Jupyter notebook environment and run the cells in:
```text
app.ipynb
```

---

## 📂 Project Structure
```text
FinanceFlow-AI/
├── app_gradio.py               # Gradio UI & Medical Analytics dashboard (Primary)
├── app.py                      # Streamlit UI & Medical Analytics dashboard (Secondary)
├── database.py                 # SQLite medical_receipts table and queries
├── app.ipynb                   # Jupyter Notebook demonstrating the pipeline inline
├── requirements.txt            # Python dependencies
├── .env                        # Local environment file (API Key)
└── utils/
    ├── __init__.py
    ├── llm_parser.py           # Gemini AI medical prompt and JSON parser
    └── preprocessing.py        # OpenCV image optimization
```

