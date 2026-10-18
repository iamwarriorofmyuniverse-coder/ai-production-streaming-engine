import json
from fastapi import APIRouter, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from app.models.schemas import ChatRequest
from app.services.llm_service import llm_service
from app.services.cache_service import cache_service
from app.core.logging import logger

router = APIRouter()

@router.post("/chat/stream", summary="Stream LLM tokens over Server-Sent Events (SSE)")
async def stream_chat_endpoint(request: Request, payload: ChatRequest):
    client_ip = request.client.host if request.client else "127.0.0.1"

    # 1. Rate Limiting Check
    if await cache_service.is_rate_limited(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please wait a moment before sending more requests."
        )

    # 2. Check Cache
    cached_response = await cache_service.get_cached_response(
        payload.prompt, payload.model, payload.temperature
    )
    if cached_response:
        logger.info(f"Cache HIT for prompt: '{payload.prompt[:30]}...'")
        async def cached_stream():
            yield f"data: {json.dumps({'token': cached_response, 'cached': True})}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(
            cached_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
        )

    logger.info(f"Cache MISS. Streaming from LLM for prompt: '{payload.prompt[:30]}...'")

    # 3. Stream from LLM & accumulate for caching
    async def sse_event_generator():
        accumulated = []
        try:
            async for token in llm_service.stream_tokens(
                prompt=payload.prompt,
                model=payload.model,
                temperature=payload.temperature,
                system_prompt=payload.system_prompt
            ):
                # Guard against client closing connection mid-stream
                if await request.is_disconnected():
                    logger.info("Client disconnected mid-stream. Halting generator.")
                    return

                accumulated.append(token)
                event_payload = json.dumps({"token": token, "cached": False})
                yield f"data: {event_payload}\n\n"

            # Cache the completed response
            full_text = "".join(accumulated)
            if full_text:
                await cache_service.set_cached_response(
                    payload.prompt, payload.model, payload.temperature, full_text
                )

            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Error during stream generation: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        sse_event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.websocket("/chat/ws")
async def chat_websocket_endpoint(websocket: WebSocket):
    """Full-duplex WebSocket streaming endpoint."""
    await websocket.accept()
    logger.info("WebSocket client connected.")
    try:
        while True:
            data = await websocket.receive_text()
            req = json.loads(data)
            prompt = req.get("prompt", "")
            
            async for token in llm_service.stream_tokens(prompt=prompt):
                await websocket.send_text(json.dumps({"token": token}))
            
            await websocket.send_text(json.dumps({"token": "[DONE]"}))
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected.")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()
