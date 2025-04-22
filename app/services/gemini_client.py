from google import genai

from app.config.settings import get_settings

settings = get_settings()


client = genai.Client(api_key=settings.GEMINI_API_KEY)
