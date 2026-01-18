
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

print("Listing models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
            
    print("\nTesting gemini-1.5-flash:")
    model = genai.GenerativeModel("gemini-1.5-flash")
    print(model.generate_content("Hello").text)
except Exception as e:
    print("Error:", e)
