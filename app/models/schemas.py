from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4000, description="User query prompt")
    model: str = Field(default="llama-3.1-8b-instant", description="Model name to use")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    system_prompt: Optional[str] = Field(default=None, description="Optional system instruction")

class ChatResponse(BaseModel):
    response: str
    cached: bool = False
    model_used: str

class HealthResponse(BaseModel):
    status: str
    version: str
    redis_connected: bool
