from datetime import datetime
from jenna import Jenna
from discord_slash import cog_ext, SlashContext
from discord.ext import commands
from discord_slash.client import SlashCommand
from discord_slash.utils.manage_commands import create_option

from cogs.common import colors
import env

from cogs.commands import avatar


class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_ids = [env.HOME_GUILD] if env.TESTING else None

    @commands.Cog.listener()
    async def on_ready(self):
        self.add_command(avatar.run, avatar.props)

    def add_command(self, function, props):
        add: SlashCommand = self.bot.slash
        add.slash(guild_ids=self.guild_ids, **props)(function)


def setup(bot):
    bot.add_cog(Slash(bot))