from discord.ext import commands
from discord.ext.commands.errors import CommandError
from .common import utils


class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def dev(self, ctx):
        pass

    @dev.command()
    async def resend(self, ctx):
        ref_msg = utils.get_referenced_message(ctx.message)
        if not ref_msg:
            raise CommandError('No reference message.')

        await ref_msg.edit(content=ref_msg.content)


def setup(bot):
    bot.add_cog(Dev(bot))
