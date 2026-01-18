import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def test_image_structure():
    # Mock image data
    image_data = b"fake-image-data"
    mime_type = "image/jpeg"
    
    # User's current structure
    image_part_user = {
        "mime_type": mime_type,
        "data": image_data
    }
    
    prompt = "What is in this image?"
    
    print("Testing user's structure...")
    try:
        # This will likely fail if structure is wrong
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[prompt, image_part_user]
        )
        print("User structure worked (unexpectedly)")
    except Exception as e:
        print(f"User structure failed as expected: {e}")

    # Correct structure using types.Part
    print("\nTesting types.Part structure...")
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[
                prompt,
                types.Part.from_bytes(data=image_data, mime_type=mime_type)
            ]
        )
        print("types.Part structure worked")
    except Exception as e:
        print(f"types.Part structure failed: {e}")

if __name__ == "__main__":
    test_image_structure()
