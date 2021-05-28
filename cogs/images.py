from .common import colors
from .common import converter as conv
from .common import utils
from discord.ext import commands
from datetime import datetime


INSPIROBOT_URL = 'http://inspirobot.me'
INSPIROBOT_API = INSPIROBOT_URL + '/api?generate=true'
async def get_inspiro_quote():
    return await utils.download(INSPIROBOT_API)

class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['ava', 'pfp'])
    async def avatar(self, ctx, *, member:conv.FuzzyMember=None):
        member = member or ctx.author
        embed = colors.embed(description=member.mention)
        embed.title = str(member)
        embed.set_image(url=str(member.avatar_url).replace('webp', 'png'))
        embed.timestamp = datetime.now().astimezone()
        await ctx.send(embed=embed)
    
    @commands.command(aliases=['quote'])
    async def inspiro(self, ctx):
        await ctx.trigger_typing()
        embed = colors.embed(title='InspiroBot', url=INSPIROBOT_URL)
        quote_image = await get_inspiro_quote()
        embed.set_image(url=quote_image)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Images(bot))