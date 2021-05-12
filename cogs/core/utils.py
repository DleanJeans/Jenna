import aiohttp
import discord
import mimetypes
import env
import requests_async as requests
from discord.ext import commands
from ..core.emotes import utils as emotes

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

async def is_owner_testing(ctx):
    return env.TESTING and await ctx.bot.is_owner(ctx.author)

async def is_user_on_local(ctx):
    return env.LOCAL and not await is_owner_testing(ctx)

def get_referenced_message(message):
    ref = message.reference
    ref_message = None
    if ref:
        ref_message = ref.cached_message or ref.resolved
        if type(ref_message) is discord.DeletedReferencedMessage:
            return
    return ref_message

def get_ref_message_text_if_no_text(message, text=''):
    if type(message) is commands.Context:
        message = message.message
    ref = get_referenced_message(message)
    if not text and ref:
        text = ref.content
    return text, ref

async def get_last_message_text_if_no_text(context, text=''):
    last_message = None
    if not text:
        last_message = await context.history(limit=1, before=context.message).flatten()
        last_message = last_message[0]
        text = last_message.content
    return text, last_message