import asyncio
import time

async def fake(prompt_id:int):
    print(f"Starting LLM call#{prompt_id}..")
    await asyncio.sleep(2)
    print(f"Finished LLm call#{prompt_id}!")
    return f"Result #{prompt_id}"

async def main():
    print("-- Starting Concurrent LLM calls ---")
    start_time=time.perf_counter()
 
    results=await asyncio.gather(
         fake(1),
         fake(2),
         fake(3),
    )
    end_time = time.perf_counter()
    total=end_time-start_time

    print(f"\nALL results:{results}")
    print(f"Total Execution Time:{total:.2f}seconds")

if __name__=="__main__":
    asyncio.run(main())