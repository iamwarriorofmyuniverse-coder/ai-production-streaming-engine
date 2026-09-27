import asyncio
import time
import httpx

async def fetch_url(url: str, client: httpx.AsyncClient):
    response = await client.get(url)
    return f"{url} -> Status: {response.status_code}, Bytes: {len(response.content)}"

async def main():
    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/2",
        "https://httpbin.org/delay/3",
    ]
    
    start = time.perf_counter()
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(*(fetch_url(url, client) for url in urls))
    
    elapsed = time.perf_counter() - start
    
    for r in results:
        print(r)
    print(f"\nTotal time: {elapsed:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())