import hashlib
import lib.lib_userdb.repository as db


async def generate_url(original_url: str) -> str:
    existing = await db.query_by_original_url(original_url)
    if existing:
        return existing["short_url"]
    short_url = await _generate_unique_short_url(original_url)
    await db.insert_url(original_url, short_url)
    return short_url


async def _generate_unique_short_url(original_url: str) -> str:
    attempt = 0
    while True:
        short_url = _hash(original_url, attempt)
        if not await db.query_by_short_url(short_url):
            return short_url
        attempt += 1


def _hash(original_url: str, attempt: int = 0) -> str:
    salted = f"{original_url}{attempt}"
    return hashlib.md5(salted.encode()).hexdigest()[:8]
