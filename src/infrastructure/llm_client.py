from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL

_client = None


def get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


async def complete(prompt: str) -> str:
    client = get_client()
    response = await client.aio.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    return response.text


async def stream_complete(prompt: str):
    client = get_client()
    response = await client.aio.models.generate_content_stream(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    async for chunk in response:
        if chunk.text:
            yield chunk.text