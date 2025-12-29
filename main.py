from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

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

    r = requests.post(url, json=payload, timeout=30)
    r.raise_for_status()

    data = r.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


@app.post("/alice")
async def alice_webhook(request: Request):
    body = await request.json()

    user_text = body["request"].get("command", "")

    if not user_text:
        answer = "Салом! Саволи худро бигӯ."
    else:
        try:
            answer = ask_gemini(user_text)
        except Exception:
            answer = "Хатогӣ шуд ҳангоми пайвастшавӣ ба Gemini."

    return {
        "version": "1.0",
        "response": {
            "text": answer,
            "end_session": False
        }
    }
