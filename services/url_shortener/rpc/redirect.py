import lib.lib_userdb.repository as db


async def redirect(short_url: str) -> str | None:
    # TODO: query Redis cache before hitting DB
    db_url = await db.query_by_short_url(short_url)
    if db_url:
        await db.increment_count(short_url)
        return db_url["original_url"]
    return None
