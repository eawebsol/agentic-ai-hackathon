import os
from google import genai
from pathlib import Path
from dotenv import load_dotenv

load_dotenv("hello_agent/.env")
client = genai.Client()
for m in client.models.list():
    if "flash" in m.name or "pro" in m.name:
        print(m.name)

