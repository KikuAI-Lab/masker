import asyncio
import time

import httpx


async def test_rate_limit():
    async with httpx.AsyncClient() as client:
        print("🚀 Starting Rate Limit Test (70 requests)...")
        start = time.time()

        # Create 70 concurrent requests
        tasks = [
            client.post("http://localhost:8000/api/v1/detect", json={"text": "test"})
            for _ in range(70)
        ]

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        success = 0
        limited = 0
        errors = 0

        for r in responses:
            if isinstance(r, Exception):
                errors += 1
                continue

            if r.status_code == 200:
                success += 1
            elif r.status_code == 429:
                limited += 1
            else:
                print(f"Unexpected: {r.status_code}")

        duration = time.time() - start
        print(f"\n📊 Results ({duration:.2f}s):")
        print(f"✅ Success: {success}")
        print(f"🛑 Rate Limited: {limited}")
        print(f"❌ Errors: {errors}")

        if limited > 0:
            print("\n✅ Rate limiting is WORKING!")
        else:
            print("\n❌ Rate limiting NOT working (or limit too high)")

if __name__ == "__main__":
    asyncio.run(test_rate_limit())
