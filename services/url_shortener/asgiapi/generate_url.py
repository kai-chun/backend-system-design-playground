from fastapi import FastAPI
from rpc.generate_url import generate_url as generate_url_service

app = FastAPI()


@app.post("/generate_url")
async def generate_url(original_url: str) -> str:
    return await generate_url_service(original_url)
