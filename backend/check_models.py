import asyncio
import os
import httpx
from dotenv import load_dotenv

async def check_models():
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("No OPENROUTER_API_KEY found")
        return

    url = "https://openrouter.ai/api/v1/models"
    headers = {"Authorization": f"Bearer {api_key}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            models = response.json().get("data", [])
            print(f"Total models: {len(models)}")
            embedding_models = [m["id"] for m in models if "embedding" in m["id"]]
            print(f"Embedding models: {embedding_models}")

            openai_embedding = [m["id"] for m in models if "text-embedding" in m["id"]]
            print(f"OpenAI embedding models on OpenRouter: {openai_embedding}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)

if __name__ == "__main__":
    asyncio.run(check_models())
