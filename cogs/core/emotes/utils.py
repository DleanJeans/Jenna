from discord.ext import commands
from ..utils import *
import re
import discord

async def to_partial_emoji(ctx, s):
    try:
        return await commands.PartialEmojiConverter().convert(ctx, s)
    except:
        print(s)

def get_url(emoji):
    if type(emoji) in [discord.Emoji, discord.PartialEmoji]:
        return emoji.url, None
    else:
        url = get_twemoji_cdn(emoji)
        single_url = get_twemoji_cdn(emoji[0])
        return url, single_url

TWEMOJI_CDN = 'https://twemoji.maxcdn.com/v/latest/72x72/%s.png'
def get_twemoji_cdn(emoji):
    return TWEMOJI_CDN % '-'.join(format(ord(char), 'x') for char in emoji)

EMOJID_PATTERN = '<(a*):[^:\s]+:(\d+)>'
def shorten(emoji):
    id = re.findall(EMOJID_PATTERN, str(emoji))
    if id:
        id = ''.join(id[0])
    return id

def expand(name, id):
    if re.findall(EMOJID_PATTERN, id):
        return id
    a = ''
    if id.startswith('a'):
        a = 'a'
        id = id[1:]
    return f'<{a}:{name}:{id}>'

async def react_tick(message):
    try:
        await message.add_reaction('✅')
    except:
        pass