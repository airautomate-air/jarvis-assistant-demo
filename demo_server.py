import os

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="Jarvis Demo API")

SYSTEM_PROMPT = (
    "You are Jarvis, a personal AI assistant. In your full form you run locally on JP's "
    "MacBook with real-time voice conversation, hand-gesture camera control, browser "
    "automation, and smart-home integration. This public demo is a text-only preview of "
    "just the conversational core - be helpful, direct, and a little witty, and if asked "
    "about your voice/vision/automation abilities, explain those only run in the local "
    "version, not here."
)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "openai/gpt-oss-20b"


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "Jarvis Demo API"}


@app.post("/api/chat")
async def chat(req: ChatRequest):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += [{"role": m.role, "content": m.content} for m in req.messages[-20:]]

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": GROQ_MODEL, "messages": messages, "temperature": 0.7},
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Groq error: {resp.text[:300]}")

    data = resp.json()
    reply = data["choices"][0]["message"]["content"]
    return {"reply": reply}


# Static frontend mount must come after the /api/* routes above (see llm-council's
# same gotcha - an earlier route at "/" would otherwise shadow this and the SPA never loads).
app.mount("/", StaticFiles(directory="static", html=True), name="static")
