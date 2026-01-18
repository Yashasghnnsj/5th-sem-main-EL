
import os
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv

# Setup
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-2.0-flash-lite')

DATA_DIR = "data"
CROPS = ["Paddy", "Ragi", "Coffee", "Sugarcane", "Potato", "Maize", "Capsicum", "Soybean", "Grape", "Orange", "Apple"]

def enhance_crop(crop_name):
    print(f"--- Starting {crop_name} ---")
    file_path = os.path.join(DATA_DIR, f"knowledge_core_{crop_name.lower()}.json")
    
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
                print(f"Loaded current data for {crop_name}")
        else:
            current_data = {"name": crop_name}
            print(f"No existing file for {crop_name}, creating new.")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        current_data = {"name": crop_name}

    prompt = f"""
    Act as an expert agricultural scientist from UAS Dharwad/IIHR Bangalore.
    Enhance the following JSON knowledge base for {crop_name} to be EXTREMELY DETAILED (Digital Herbarium Quality).
    
    Core Objectives:
    1. Lifecycle: Detailed phases (at least 6: Nursery/Sowing, Vegetative, Flowering, Fruit/Grain Initiation, Maturity, Post-Harvest).
    2. Procedures: Comprehensive, step-by-step agricultural operations for each phase (Fertigation, Integrated Pest Management, specific pruning/weeding techniques).
    3. Disease Protocols: DETAIL AT LEAST 8 major diseases (Fungal, Bacterial, Viral, Phytoplasma).
    4. Cures: Specific Organic AND Chemical cures with exact dosages (e.g., '2ml Propiconazole in 1L water').
    
    Context: {json.dumps(current_data)}
    
    RETURN ONLY THE RAW JSON CONTENT. NO MARKDOWN, NO EXPLANATIONS.
    """

    try:
        print(f"Sending prompt to Gemini for {crop_name}...")
        response = model.generate_content(prompt)
        text = response.text.strip()
        print(f"Received response from Gemini (length: {len(text)})")
        
        # Clean markdown
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        # Validate JSON
        new_data = json.loads(text.strip())
        print(f"Validated JSON for {crop_name}")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=2)
            
        print(f"Successfully updated {crop_name} file: {file_path}")
    except Exception as e:
        print(f"Error [{crop_name}]: {type(e).__name__} - {str(e)[:100]}")
        if 'text' in locals() and text:
             print(f"Text tail: {text[-100:]}")

if __name__ == "__main__":
    for crop in CROPS:
        enhance_crop(crop)
        # Longer sleep to avoid rate limits
        time.sleep(5)
