import os
from google import genai
from dotenv import load_dotenv

# Load environment variables from the root .env file
env_path = os.path.join(os.path.dirname(__file__), "../../../.env")
load_dotenv(dotenv_path=env_path)

API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(
    api_key=API_KEY
)

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="What is Retrieval Augmented Generation?"
)

print(response.text)