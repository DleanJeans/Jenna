import env

from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash.client import SlashCommand

from cogs.commands import avatar


class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_ids = [env.HOME_GUILD] if env.TESTING else None

    @commands.Cog.listener()
    async def on_ready(self):
        self.slash = SlashCommand(self.bot, sync_commands=True, sync_on_cog_reload=True)
        self.add_command(avatar.send, avatar.props)

    def add_command(self, function, props):
        add: SlashCommand = self.slash
        add.slash(guild_ids=self.guild_ids, **props)(function)


def setup(bot):
    bot.add_cog(Slash(bot))