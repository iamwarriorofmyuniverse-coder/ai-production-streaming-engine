# ⚡ Production AI Streaming Engine

An asynchronous, resilient AI backend engine built using **FastAPI**, **Server-Sent Events (SSE)**, **SHA-256 Response Caching**, and **Sliding-Window Rate Limiting**.

---

## 🌟 Key Architecture & Features

1. **Asynchronous Non-Blocking Concurrency**: Powered by Python `asyncio` and `httpx.AsyncClient`.
2. **Real-Time Token Streaming**: Streams tokens chunk-by-chunk over standard Server-Sent Events (`text/event-stream`).
3. **Client Disconnect Guard**: Automatically halts upstream token generation if a user closes the browser tab, saving compute.
4. **Exact-Match Response Caching**: SHA-256 hashed prompt caching delivering sub-5ms responses for repeated queries ($0.00 cost).
5. **Sliding-Window Rate Limiter**: IP-level throttling protecting endpoints against abuse (HTTP 429).

---

## 📁 Repository Structure

```text
├── 01_async_demo.py            # Python asyncio event loops & parallelism
├── 02_real_async_http.py        # Non-blocking async network I/O with httpx
├── 03_fastapi_hello.py         # REST API with Pydantic v2 data validation
├── 04_streaming_sse.py         # Token streaming with Server-Sent Events (SSE)
├── 05_real_llm_stream.py       # Live LLM stream with client disconnect guard
├── 06_caching_and_rate_limit.py # Full engine with SHA-256 caching & rate limiting
├── .env.example                # Environment variables template
└── README.md
```

---

## 🛠️ How to Run

### 1. Install Dependencies
```bash
pip install fastapi uvicorn pydantic httpx python-dotenv
```

### 2. Configure Environment (Optional)
```bash
cp .env.example .env
# Add your GROQ_API_KEY if desired
```

### 3. Run the Engine
```bash
python 06_caching_and_rate_limit.py
```

### 4. Test with cURL
```bash
curl.exe -N -X POST "http://127.0.0.1:8000/api/v1/chat" -H "Content-Type: application/json" -d "{\"prompt\": \"What is Python?\"}"
```