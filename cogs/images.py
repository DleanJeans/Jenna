import discord
import colors

from discord.ext import commands
from datetime import datetime
from .core import converter as conv
from .core import utils

INSPIROBOT_URL = 'http://inspirobot.me'
INSPIROBOT_API = INSPIROBOT_URL + '/api?generate=true'
async def get_inspiro_quote():
    return await utils.download(INSPIROBOT_API)

class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['ava', 'pfp'])
    @commands.guild_only()
    async def avatar(self, context, *, member:conv.FuzzyMember=None):
        member = member or context.author
        embed = colors.embed(description=member.mention)
        embed.title = str(member)
        embed.set_image(url=str(member.avatar_url).replace('webp', 'png'))
        embed.timestamp = datetime.now().astimezone()
        await context.send(embed=embed)
    
    @commands.command(aliases=['quote'])
    async def inspiro(self, context):
        await context.trigger_typing()
        embed = colors.embed(title='InspiroBot', url=INSPIROBOT_URL)
        quote_image = await get_inspiro_quote()
        embed.set_image(url=quote_image)
        await context.send(embed=embed)

def setup(bot):
    bot.add_cog(Images(bot))