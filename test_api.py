import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("API Key not found in .env!")
    exit(1)

genai.configure(api_key=API_KEY)

try:
    print("Available models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
            
    print("\nAttempting to generate with gemini-1.5-pro...")
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content("Hello, just testing.")
    print("Response:", response.text)
except Exception as e:
    print(f"Error testing model: {e}")
