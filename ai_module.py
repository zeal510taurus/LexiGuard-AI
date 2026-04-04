import os
import google.generativeai as genai

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("Please set your GOOGLE_API_KEY environment variable")

genai.configure(api_key=API_KEY)

def ask_ai(prompt):
    return genai.generate_text(model="models/text-bison-001", prompt=prompt).text