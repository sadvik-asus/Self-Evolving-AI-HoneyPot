import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

try:
    print("Testing gemini-flash-lite-latest...")
    model = genai.GenerativeModel('gemini-flash-lite-latest')
    response = model.generate_content("Hello, this is a test.")
    print("Response:", response.text)
except Exception as e:
    print(f"Exception: {e}")
