import os
from dotenv import load_dotenv

from google import genai

# Load environment variables from .env
load_dotenv()

# Get API key
api_key = os.getenv("GEMINI_API_KEY")


client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain how AI works in a few words",
)

print(response.text)