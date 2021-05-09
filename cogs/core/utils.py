import aiohttp
import mimetypes
import requests_async as requests
from discord.ext import commands

def url_is_image(url):
    mimetype, encoding = mimetypes.guess_type(url)
    return 'image' in str(mimetype)

READ = 'read'
async def download(url, method='text'):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                if method:
                    return await getattr(resp, method)()
                return resp

async def request(url, method=''):
    response = await requests.get(url)
    if method == READ:
        return response.content
    else:
        return response.text

def is_owner_testing():
    async def predicate(ctx):
        if not await ctx.bot.is_owner(ctx.author):
            raise NotOwner('You do not own this bot.')
        return env.TESTING

    return commands.check(predicate)