import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("Please set your GOOGLE_API_KEY in the .env file")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

def ask_ai(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"