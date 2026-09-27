import asyncio
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="My First AI API", version="1.0.0")

class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=3, description="User question or prompt")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "AI Backend Engine"}

@app.post("/api/v1/generate")
async def generate(request: GenerateRequest):
    await asyncio.sleep(1)
    return {
        "prompt_received": request.prompt,
        "temperature_used": request.temperature,
        "generated_answer": f"Simulated AI response to '{request.prompt}'",
        "tokens_count": len(request.prompt.split()) + 15,
        "status": "completed"
    }