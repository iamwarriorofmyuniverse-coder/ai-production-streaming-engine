import asyncio
import json
import uvicorn
import httpx
import os
from dotenv import load_dotenv
from typing import AsyncGenerator
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# Automatically load environment variables from .env file
load_dotenv()

app = FastAPI(title="Real LLM Streaming Engine", version="1.0.0")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = os.getenv("GROQ_URL", "https://api.groq.com/openai/v1/chat/completions")

class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="Question for the LLM")
    model: str = Field(default="llama-3.1-8b-instant", description="Model name")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)

async def stream_groq_llm(prompt: str, model: str, temperature: float) -> AsyncGenerator[str, None]:
    """Streams live tokens from Groq (Llama 3.1) or fallback simulator."""
    
    # 1. If valid key exists, query real Groq API
    if GROQ_API_KEY and GROQ_API_KEY.startswith("gsk_"):
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
            "temperature": temperature
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("POST", GROQ_URL, headers=headers, json=payload) as response:
                if response.status_code == 200:
                    async for line in response.aiter_lines():
                        if not line or line.startswith(":"):
                            continue
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            if data_str == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data_str)
                                delta = chunk["choices"][0]["delta"].get("content", "")
                                if delta:
                                    yield delta
                            except json.JSONDecodeError:
                                continue
                    return

    # 2. Fallback Smart Simulator if key not yet configured
    fallback_text = (
        f"Quantum computing utilizes quantum mechanics principles like superposition and entanglement "
        f"to process complex information exponentially faster than classical computers."
    )
    for word in fallback_text.split(" "):
        yield word + " "
        await asyncio.sleep(0.06)

@app.post("/api/v1/chat")
async def chat_endpoint(request: Request, body: ChatRequest):
    async def event_generator():
        try:
            async for token in stream_groq_llm(body.prompt, body.model, body.temperature):
                # 🛡️ Disconnect Guard: Stops wasting compute if user closes connection
                if await request.is_disconnected():
                    print("⚠️ Client disconnected! Halting stream.")
                    return

                event_data = json.dumps({"token": token})
                yield f"data: {event_data}\n\n"

            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

if __name__ == "__main__":
    uvicorn.run("05_real_llm_stream:app", host="127.0.0.1", port=8000, reload=True)