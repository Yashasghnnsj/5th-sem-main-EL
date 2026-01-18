import os
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime

# Setup
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('models/gemini-2.0-flash-lite')

DATA_DIR = "data"
# All crops that need upgrading
ALL_CROPS = ["Paddy", "Ragi", "Coffee", "Sugarcane", "Potato", "Maize", "Capsicum", "Soybean", "Grape", "Orange", "Apple"]

# Track which crops need upgrading (sizes less than 10KB)
SMALL_SIZE_THRESHOLD = 10000  # 10KB

def needs_upgrade(crop_name):
    """Check if a crop's knowledge base needs upgrading based on file size"""
    file_path = os.path.join(DATA_DIR, f"knowledge_core_{crop_name.lower()}.json")
    if not os.path.exists(file_path):
        return True
    file_size = os.path.getsize(file_path)
    return file_size < SMALL_SIZE_THRESHOLD

def enhance_crop(crop_name, retry_delay=60):
    """Enhance a single crop with retry logic"""
    print(f"\n{'='*60}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Processing: {crop_name}")
    print(f"{'='*60}")
    
    file_path = os.path.join(DATA_DIR, f"knowledge_core_{crop_name.lower()}.json")
    
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
                print(f"✓ Loaded existing data for {crop_name}")
        else:
            current_data = {"name": crop_name}
            print(f"ℹ Creating new knowledge base for {crop_name}")
    except Exception as e:
        print(f"✗ Error reading {file_path}: {e}")
        current_data = {"name": crop_name}

    prompt = f"""
    Act as an expert agricultural scientist from UAS Dharwad/IIHR Bangalore.
    Enhance the following JSON knowledge base for {crop_name} to be EXTREMELY DETAILED (Digital Herbarium Quality).
    
    Core Objectives:
    1. Lifecycle: Detailed phases (at least 6: Nursery/Sowing, Vegetative, Flowering, Fruit/Grain Initiation, Maturity, Post-Harvest).
    2. Procedures: Comprehensive, step-by-step agricultural operations for each phase (Fertigation, Integrated Pest Management, specific pruning/weeding techniques).
    3. Disease Protocols: DETAIL AT LEAST 8 major diseases (Fungal, Bacterial, Viral, Phytoplasma).
    4. Cures: Specific Organic AND Chemical cures with exact dosages (e.g., '2ml Propiconazole in 1L water').
    
    IMPORTANT: Return symptoms as an ARRAY, not a string. Example:
    "symptoms": ["symptom 1", "symptom 2", "symptom 3"]
    
    Context: {json.dumps(current_data)}
    
    RETURN ONLY THE RAW JSON CONTENT. NO MARKDOWN, NO EXPLANATIONS.
    """

    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"→ Sending request to Gemini (Attempt {attempt + 1}/{max_retries})...")
            response = model.generate_content(prompt)
            text = response.text.strip()
            print(f"✓ Received response ({len(text)} characters)")
            
            # Clean markdown
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            
            # Validate JSON
            new_data = json.loads(text.strip())
            print(f"✓ JSON validated successfully")
            
            # Verify disease structure
            if "disease_protocols" in new_data:
                for disease_id, disease_data in new_data["disease_protocols"].items():
                    if "symptoms" in disease_data and isinstance(disease_data["symptoms"], str):
                        # Convert string symptoms to array
                        disease_data["symptoms"] = [disease_data["symptoms"]]
                        print(f"  ⚠ Fixed symptoms format for {disease_id}")
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, indent=2)
            
            file_size = os.path.getsize(file_path)
            print(f"✓ SUCCESS! Updated {crop_name} ({file_size:,} bytes)")
            return True
            
        except Exception as e:
            error_msg = str(e)
            if "ResourceExhausted" in error_msg or "429" in error_msg or "quota" in error_msg.lower():
                print(f"⚠ Quota limit reached")
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (attempt + 1)
                    print(f"  Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    print(f"✗ Failed after {max_retries} attempts (quota exceeded)")
                    return False
            else:
                print(f"✗ Error: {type(e).__name__} - {str(e)[:200]}")
                return False
    
    return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("KNOWLEDGE BASE ENHANCEMENT - SMART RETRY MODE")
    print("="*60)
    
    # Identify crops that need upgrading
    crops_to_upgrade = [crop for crop in ALL_CROPS if needs_upgrade(crop)]
    
    print(f"\nCrops requiring upgrade: {len(crops_to_upgrade)}/{len(ALL_CROPS)}")
    for crop in crops_to_upgrade:
        file_path = os.path.join(DATA_DIR, f"knowledge_core_{crop.lower()}.json")
        size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        print(f"  - {crop}: {size:,} bytes")
    
    if not crops_to_upgrade:
        print("\n✓ All crops are already upgraded!")
        exit(0)
    
    print(f"\nStarting enhancement process...")
    print(f"Strategy: Process one crop at a time with 60s base retry delay")
    
    success_count = 0
    failed_crops = []
    
    for i, crop in enumerate(crops_to_upgrade):
        success = enhance_crop(crop, retry_delay=60)
        
        if success:
            success_count += 1
        else:
            failed_crops.append(crop)
        
        # Wait between crops (except for the last one)
        if i < len(crops_to_upgrade) - 1:
            print(f"\n⏳ Waiting 10 seconds before next crop...")
            time.sleep(10)
    
    # Summary
    print("\n" + "="*60)
    print("ENHANCEMENT SUMMARY")
    print("="*60)
    print(f"✓ Successfully upgraded: {success_count}/{len(crops_to_upgrade)}")
    if failed_crops:
        print(f"✗ Failed crops: {', '.join(failed_crops)}")
        print(f"\nTo retry failed crops, run this script again.")
    else:
        print("🎉 All crops upgraded successfully!")
