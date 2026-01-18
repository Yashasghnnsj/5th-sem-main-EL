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
model = genai.GenerativeModel('models/gemini-2.5-flash-lite')

DATA_DIR = "data"
SMALL_SIZE_THRESHOLD = 10000  # 10KB - crops below this need upgrading

def get_next_crop_to_upgrade():
    """Find the next crop that needs upgrading"""
    all_crops = ["Paddy", "Ragi", "Coffee", "Sugarcane", "Potato", "Maize", "Capsicum", "Soybean", "Grape", "Orange", "Apple"]
    
    for crop in all_crops:
        file_path = os.path.join(DATA_DIR, f"knowledge_core_{crop.lower()}.json")
        if not os.path.exists(file_path):
            return crop
        file_size = os.path.getsize(file_path)
        if file_size < SMALL_SIZE_THRESHOLD:
            return crop
    
    return None

def enhance_single_crop(crop_name):
    """Enhance ONE crop with patient retry logic"""
    print(f"\n{'='*70}")
    print(f"🌱 UPGRADING: {crop_name}")
    print(f"{'='*70}\n")
    
    file_path = os.path.join(DATA_DIR, f"knowledge_core_{crop_name.lower()}.json")
    
    # Load current data
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
                print(f"✓ Loaded existing {crop_name} data ({os.path.getsize(file_path)} bytes)")
        else:
            current_data = {"name": crop_name}
            print(f"ℹ Creating new knowledge base for {crop_name}")
    except Exception as e:
        print(f"⚠ Error reading file: {e}")
        current_data = {"name": crop_name}

    # Prepare enhancement prompt
    prompt = f"""
    Act as an expert agricultural scientist from UAS Dharwad/IIHR Bangalore.
    Enhance the following JSON knowledge base for {crop_name} to be EXTREMELY DETAILED (Digital Herbarium Quality).
    
    CRITICAL REQUIREMENTS:
    1. Lifecycle: At least 6 detailed phases (Nursery/Sowing, Vegetative, Flowering, Fruit/Grain Initiation, Maturity, Post-Harvest)
    2. Procedures: 6-8 step-by-step operations per phase with specific NPK doses, irrigation schedules, pest management
    3. Disease Protocols: Minimum 8 major diseases with:
       - Full scientific name
       - "symptoms" field MUST be an ARRAY: ["symptom 1", "symptom 2", "symptom 3"]
       - "favorable_conditions" string explaining temperature, humidity, etc.
       - "preventive_measures" array of cultural practices
       - "management_procedures" with both "organic" and "chemical" arrays containing specific products and dosages
    
    Current data: {json.dumps(current_data)}
    
    RETURN ONLY RAW JSON. NO MARKDOWN CODE BLOCKS. NO EXPLANATIONS.
    """

    # Retry with exponential backoff
    max_attempts = 5
    base_wait = 90  # Start with 90 seconds
    
    for attempt in range(max_attempts):
        try:
            wait_time = base_wait * (2 ** attempt)  # Exponential: 90, 180, 360, 720, 1440 seconds
            
            if attempt > 0:
                print(f"\n⏳ Retry #{attempt} - Waiting {wait_time} seconds for quota refresh...")
                time.sleep(wait_time)
            
            print(f"→ Sending request to Gemini (Attempt {attempt + 1}/{max_attempts})...")
            response = model.generate_content(prompt)
            text = response.text.strip()
            
            print(f"✓ Received response ({len(text)} characters)")
            
            # Clean markdown artifacts
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            
            # Validate and parse JSON
            new_data = json.loads(text.strip())
            print(f"✓ JSON structure validated")
            
            # Ensure symptoms are arrays
            if "disease_protocols" in new_data:
                diseases_fixed = 0
                for disease_id, disease_data in new_data["disease_protocols"].items():
                    if "symptoms" in disease_data:
                        if isinstance(disease_data["symptoms"], str):
                            disease_data["symptoms"] = [disease_data["symptoms"]]
                            diseases_fixed += 1
                        elif not isinstance(disease_data["symptoms"], list):
                            disease_data["symptoms"] = ["Data structure error"]
                            diseases_fixed += 1
                
                if diseases_fixed > 0:
                    print(f"✓ Fixed {diseases_fixed} disease symptom formats")
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, indent=2)
            
            final_size = os.path.getsize(file_path)
            print(f"\n🎉 SUCCESS! {crop_name} upgraded to {final_size:,} bytes")
            print(f"   (Previous: {os.path.getsize(file_path):,} bytes)\n")
            
            return True
            
        except Exception as e:
            error_str = str(e)
            
            if "ResourceExhausted" in error_str or "429" in error_str or "quota" in error_str.lower():
                print(f"⚠ API quota limit hit")
                if attempt < max_attempts - 1:
                    next_wait = base_wait * (2 ** (attempt + 1))
                    print(f"   Will retry in {next_wait} seconds...")
                else:
                    print(f"\n✗ Failed after {max_attempts} attempts")
                    print(f"   The API quota is exhausted.")
                    print(f"   💡 Solution: Run this script again in 1 hour to complete {crop_name}")
                    return False
            else:
                print(f"\n✗ Unexpected Error: {type(e).__name__}")
                print(f"   {str(e)[:300]}")
                if 'text' in locals() and text:
                    print(f"\n   Response preview: {text[:200]}...")
                return False
    
    return False

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 KNOWLEDGE BASE UPGRADE - SINGLE CROP MODE")
    print("="*70)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Find next crop
    next_crop = get_next_crop_to_upgrade()
    
    if next_crop is None:
        print("✅ ALL CROPS ARE ALREADY UPGRADED!")
        print(f"\n📊 All knowledge bases are ≥10KB and ready for production.\n")
    else:
        print(f"📋 Next crop to upgrade: {next_crop}")
        print()
        
        # Upgrade it
        success = enhance_single_crop(next_crop)
        
        # Summary
        print("="*70)
        if success:
            print("✅ UPGRADE COMPLETE")
            
            remaining = get_next_crop_to_upgrade()
            if remaining:
                print(f"\n💡 Next crop to upgrade: {remaining}")
                print(f"   Run this script again to continue!")
            else:
                print(f"\n🎉 ALL CROPS NOW UPGRADED!")
        else:
            print("⚠ UPGRADE INCOMPLETE")
            print(f"\n💡 To complete {next_crop}:")
            print(f"   - Wait 1 hour for API quota to refresh")
            print(f"   - Run: python upgrade_one_crop.py")
        
        print("="*70)
    
    print()
