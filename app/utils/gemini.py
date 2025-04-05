from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

async def get_gemini_response(prompt: str) -> str:
    """
    Send a prompt to Gemini API and return the response.
    """
    if not GEMINI_API_KEY:
        raise Exception("Gemini API key is not configured")

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")  # Fast and efficient model
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")