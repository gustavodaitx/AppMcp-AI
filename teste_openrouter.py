import os
import requests
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("OPENROUTER_API_KEY", "").strip()

print("Chave carregada:", repr(key[:20]) + "...")

headers = {
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json",
}

payload = {
    "model": "liquid/lfm-2.5-1.2b-thinking:free",
    "messages": [
        {
            "role": "user",
            "content": "Responda apenas OK"
        }
    ]
}
print("Modelo:", os.getenv("OPENROUTER_MODEL"))
response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers=headers,
    json=payload,
    timeout=60
)

print("Status:", response.status_code)
print("Resposta:")
print(response.text)