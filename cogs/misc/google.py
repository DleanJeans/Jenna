import discord
import random
from common.googlesearch import search
from urllib.parse import urlparse

TITLE_TEMPLATE = 'Google Search | {}'
GOOGLE_SEARCH = 'Google Search'
GOOGLE_URL_TEMPLATE = 'https://www.google.com/search?q={}'
GOOGLE_ICON = 'https://www.google.com/favicon.ico'
GOOGLE_COLORS = [0x4285F4, 0xDB4437, 0xF4B400, 0x0F9D58]


async def run_command(ctx, query):
    results = await search(query, 1)

    url = GOOGLE_URL_TEMPLATE.format(query).replace(' ', '+')
    color = random.choice(GOOGLE_COLORS)
    embed = discord.Embed(title=query, url=url, color=color)
    embed.set_author(name=GOOGLE_SEARCH, icon_url=GOOGLE_ICON)

    for page in results:
        domain = urlparse(page.link).netloc
        domain = f'({domain})' if domain else ''
        markdown_title = f'**[{page.title}]({page.link})** {domain}' if page.link else f'**{page.title}**'
        embed.description = markdown_title
        if page.preview:
            embed.description += f'\n{page.preview}'
        break

    await ctx.send(embed=embed)