import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY .env dosyasında bulunamadı.")

client = OpenAI(api_key=api_key)

SYSTEM_PROMPT = (BASE_DIR / "system_prompt.txt").read_text(
    encoding="utf-8"
)

app = FastAPI(title="Travel Chatbot API")


class ChatRequest(BaseModel):
    input: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    output: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request.input},
            ],
            temperature=0,
            max_tokens=350,
        )

        answer = response.choices[0].message.content

        return {"output": answer or "Yanıt oluşturulamadı."}

    except Exception as exc:
        print(f"OpenAI API hatası: {type(exc).__name__}")
        raise HTTPException(
            status_code=502,
            detail="Chatbot şu anda yanıt oluşturamadı."
        )