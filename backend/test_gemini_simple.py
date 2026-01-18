
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print("API Key missing")
else:
    genai.configure(api_key=API_KEY)
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content("Test")
        print("Success:", response.text)
    except Exception as e:
        print("Error:", str(e))
