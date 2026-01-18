import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def verify_flash():
    print("Flash models found:")
    models = genai.list_models()
    for m in models:
        if "flash" in m.name.lower():
            print(m.name)

if __name__ == "__main__":
    verify_flash()
