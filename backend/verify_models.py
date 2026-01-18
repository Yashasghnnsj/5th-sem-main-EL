import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def verify_models():
    print("Verifying model availability...")
    models = [m.name for m in genai.list_models()]
    
    target_models = [
        "models/gemini-1.5-flash",
        "models/gemini-1.5-pro",
        "models/gemini-1.5-flash-latest",
        "models/gemini-2.0-flash-exp"
    ]
    
    for target in target_models:
        if target in models:
            print(f"MATCH FOUND: {target}")
        else:
            print(f"NOT FOUND: {target}")
            
    print(f"Total models available: {len(models)}")

if __name__ == "__main__":
    verify_models()
