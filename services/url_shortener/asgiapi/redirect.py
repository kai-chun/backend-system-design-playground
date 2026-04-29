from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from rpc.redirect import redirect as redirect_service

app = FastAPI()


@app.get("/{short_url}")
async def redirect(short_url: str) -> RedirectResponse:
    original_url = await redirect_service(short_url)
    if original_url is None:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return RedirectResponse(original_url)
