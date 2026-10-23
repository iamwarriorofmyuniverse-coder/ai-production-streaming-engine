import hashlib
import time
import redis.asyncio as redis
from typing import Optional
from app.core.config import settings
from app.core.logging import logger

class CacheService:
    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self._in_memory_cache = {}
        self._rate_limits = {}

    async def connect(self):
        """Attempts connection to Redis, logs status."""
        try:
            self._redis = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=2.0
            )
            await self._redis.ping()
            logger.info("Connected to Redis successfully.")
        except Exception as e:
            logger.warning(f"Redis unavailable ({e}). Falling back to in-memory cache.")
            self._redis = None

    async def close(self):
        if self._redis:
            await self._redis.close()

    def _generate_cache_key(self, prompt: str, model: str, temperature: float) -> str:
        raw = f"{model}:{temperature}:{prompt.strip().lower()}"
        return f"cache:llm:{hashlib.sha256(raw.encode()).hexdigest()}"

    async def get_cached_response(self, prompt: str, model: str, temperature: float) -> Optional[str]:
        key = self._generate_cache_key(prompt, model, temperature)
        if self._redis:
            try:
                return await self._redis.get(key)
            except Exception:
                pass
        
        # In-memory fallback
        item = self._in_memory_cache.get(key)
        if item and item["expires_at"] > time.time():
            return item["val"]
        return None

    async def set_cached_response(self, prompt: str, model: str, temperature: float, full_response: str):
        key = self._generate_cache_key(prompt, model, temperature)
        if self._redis:
            try:
                await self._redis.setex(key, settings.CACHE_TTL_SECONDS, full_response)
                return
            except Exception:
                pass
        
        # In-memory fallback
        self._in_memory_cache[key] = {
            "val": full_response,
            "expires_at": time.time() + settings.CACHE_TTL_SECONDS
        }

    async def is_rate_limited(self, client_ip: str) -> bool:
        """Atomic sliding window / counter rate limiter per IP using Lua script."""
        key = f"rate_limit:{client_ip}"
        if self._redis:
            try:
                # Atomic INCR and EXPIRE in a single Lua execution
                lua_script = """
                local current = redis.call('INCR', KEYS[1])
                if current == 1 then
                    redis.call('EXPIRE', KEYS[1], ARGV[1])
                end
                return current
                """
                current = await self._redis.eval(lua_script, 1, key, 60)
                return int(current) > settings.RATE_LIMIT_PER_MINUTE
            except Exception as e:
                logger.warning(f"Redis rate limiting error ({e}). Falling back to in-memory.")
        
        # In-memory fallback rate limiter
        now = time.time()
        record = self._rate_limits.get(client_ip, {"count": 0, "reset_at": now + 60})
        if now > record["reset_at"]:
            record = {"count": 1, "reset_at": now + 60}
        else:
            record["count"] += 1
            
        self._rate_limits[client_ip] = record
        return record["count"] > settings.RATE_LIMIT_PER_MINUTE

    async def is_healthy(self) -> bool:
        if self._redis:
            try:
                return await self._redis.ping()
            except Exception:
                return False
        return False

cache_service = CacheService()
