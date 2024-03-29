from typing import Union

from discord.member import Member
from .common import colors
from .common import converter as conv
from .common import utils
from discord.ext import commands

from commands import avatar

INSPIROBOT_URL = 'http://inspirobot.me'
INSPIROBOT_API = INSPIROBOT_URL + '/api?generate=true'


async def get_inspiro_quote():
    return await utils.download(INSPIROBOT_API)


class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['ava', 'pfp'])
    async def avatar(self, ctx, *, member: Union[Member, str] = None):
        using_fuzzy_string = type(member) is str
        if using_fuzzy_string:
            member = await conv.FuzzyMember().convert(ctx, member)

        send = avatar.send_with_announcement if using_fuzzy_string else avatar.send
        await send(ctx, member)

    @commands.command(aliases=['quote'])
    async def inspiro(self, ctx):
        await ctx.trigger_typing()
        embed = colors.embed(title='InspiroBot', url=INSPIROBOT_URL)
        quote_image = await get_inspiro_quote()
        embed.set_image(url=quote_image)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Images(bot))