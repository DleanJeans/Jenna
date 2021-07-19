import aiohttp


async def request(method, url, **kwargs):
    async with aiohttp.ClientSession() as session:
        return await session.request(method=method, url=url, **kwargs)


async def get(url, params=None, **kwargs):
    kwargs.setdefault("allow_redirects", True)
    return await request("get", url, params=params, **kwargs)