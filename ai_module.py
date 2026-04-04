import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Security: Load the API Key from environment variables
# This ensures your key never touches GitHub.
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    # We raise a clear error so you don't wonder why the app is broken
    raise ValueError("❌ SECURITY ERROR: GOOGLE_API_KEY not found in environment variables.")

# 2. Configuration: Initialize the Gemini Engine
genai.configure(api_key=API_KEY)

# 3. Model Settings: Using the high-performance Gemini 2.5 Flash
# Flash is best for RAG because it is fast and has a massive context window.
generation_config = {
    "temperature": 0.2,  # Low temperature = high accuracy (less "creativity", more "fact")
    "top_p": 0.95,
    "max_output_tokens": 2048,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", # Or "gemini-2.0-flash" if available in your tier
    generation_config=generation_config,
)

def ask_ai(prompt: str) -> str:
    """
    The core engine for LexiGuard.
    Sends a structured prompt to Gemini and returns a clean string.
    """
    try:
        # Start a chat session for better coherence
        chat_session = model.start_chat(history=[])
        
        response = chat_session.send_message(prompt)
        
        if response and response.text:
            return response.text.strip()
        else:
            return "⚠️ The AI was unable to generate a response. Please check the document content."

    except Exception as e:
        # Professional Error Handling
        error_msg = str(e)
        if "quota" in error_msg.lower():
            return "🚫 Rate limit reached. Please wait a moment before asking again."
        elif "api_key" in error_msg.lower():
            return "🔑 Invalid API Key. Please check your security settings."
        else:
            return f"⚙️ AI Engine Error: {error_msg}"

def get_risk_assessment_prompt(context: str) -> str:
    """
    A helper function to wrap document context into a 'Professional Persona'
    to ensure the AI acts like a high-level auditor.
    """
    return f"""
    SYSTEM INSTRUCTION: 
    You are LexiGuard AI, a world-class Legal & Compliance Auditor. 
    Analyze the following document snippets and identify the top 3 high-priority risks.
    Format your response with bold headers and clear bullet points.
    
    DOCUMENT CONTEXT:
    {context}
    
    EXECUTIVE REQUIREMENT:
    Provide a concise, neutral, and factual risk summary.
    """