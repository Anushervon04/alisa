from fastapi import FastAPI, Request
import requests
import os
import logging

app = FastAPI()

# Logging қӯшед барои дидани хатогиҳо
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def ask_gemini(prompt: str) -> str:
    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-pro:generateContent"
        f"?key={GEMINI_API_KEY}"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        r = requests.post(url, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        
        # Safe parsing: агар "candidates" набошад, хатогӣ надиҳад
        if "candidates" in data and data["candidates"]:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            logger.error("Жавоби нодуруст аз Gemini: %s", data)
            return "Жавоби нодуруст аз Gemini."
    
    except requests.exceptions.RequestException as e:
        logger.error("Хатогӣ дар пайвастшавӣ: %s", str(e))
        return "Хатогӣ шуд ҳангоми пайвастшавӣ ба Gemini."

@app.post("/alice")
async def alice_webhook(request: Request):
    body = await request.json()

    user_text = body["request"].get("command", "")

    if not user_text:
        answer = "Салом! Саволи худро бигӯ."
    else:
        answer = ask_gemini(user_text)

    return {
        "version": "1.0",
        "response": {
            "text": answer,
            "end_session": False
        }
    }