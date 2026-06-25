import os
import json
import base64
import io
import requests
from google import genai
from PIL import Image
import numpy as np
import cv2

def extract_medical_data(image_np, provider="gemini", ollama_model="llama3.2-vision", ollama_url="http://localhost:11434"):
    # Convert numpy array to PIL Image
    if len(image_np.shape) == 2:
        # Grayscale
        img_pil = Image.fromarray(image_np).convert('RGB')
    else:
        # If it's BGR from OpenCV, convert to RGB
        img_rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
            
    # System prompt for medical receipts
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
                "dosage": "Dosage instructions, frequency, or quantity (e.g., '500mg, twice a day for 5 days', 'Qty: 2', '1 tablet daily'). If none, return null",
                "price": "Price of this medicine or service as a string (e.g., '150.00'). If not listed, return null"
            }
        ]
    }
    If a value is missing or unreadable, return null or a default value as specified above.
    Return ONLY valid JSON. Do not include markdown formatting like ```json.
    """
    
    if provider == "ollama":
        try:
            # Convert PIL image to base64
            buffered = io.BytesIO()
            img_pil.save(buffered, format="JPEG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            # Call Ollama API
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
            
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            response_json = response.json()
            
            # Extract content from response
            text = response_json.get("message", {}).get("content", "").strip()
            
            # Clean up potential markdown wrapped around json
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
                
            data = json.loads(text.strip())
            return data
            
        except Exception as e:
            return {"error": f"Ollama Error: {str(e)}"}
            
    else:  # Gemini default
        # Retrieve API key dynamically
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return {"error": "API Key not found. Please check your .env file."}
            
        from google.genai import errors
        import time
        
        try:
            client = genai.Client(api_key=api_key)
            
            models_to_try = ['gemini-2.5-flash', 'gemini-1.5-flash']
            response = None
            last_error = None
            
            for model_name in models_to_try:
                for attempt in range(3):  # up to 3 attempts with backoff
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=[prompt, img_pil]
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
                return {"error": f"Gemini API request failed: {str(last_error)}"}
                
            text = response.text.strip()
            
            # Clean up markdown if Gemini includes it despite the prompt
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
                
            data = json.loads(text.strip())
            return data
        except Exception as e:
            return {"error": str(e)}

