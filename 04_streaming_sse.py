import asyncio
import json
import uvicorn
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Real-Time AI Streaming API", version="1.0.0")

class StreamRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="Question for the AI")

async def generate_tokens(prompt: str) -> AsyncGenerator[str, None]:
    full_text = f"Hello! You asked: '{prompt}'. Here is your real-time token-by-token streamed response generated asynchronously by your FastAPI engine."

    for word in full_text.split(" "):
        payload = json.dumps({"token": word + " "})
        yield f"data: {payload}\n\n"
        await asyncio.sleep(0.08)

    yield "data: [DONE]\n\n"

@app.post("/api/v1/stream")
async def stream_endpoint(request: StreamRequest):
    return StreamingResponse(
        generate_tokens(request.prompt),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )

if __name__ == "__main__":
    uvicorn.run("04_streaming_sse:app", host="127.0.0.1", port=8000, reload=True)