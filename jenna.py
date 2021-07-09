import env

from discord import Activity, ActivityType
from discord.ext import commands

LOGGED_IN = 'Logged in as'
TESTING_MSG = 'Jennie is up and running'
PROD_MSG = "I'm ready to go!"
HELP_COMMAND = 'j help'


class Jenna(commands.Bot):
    async def on_ready(self):
        await self.set_activity_to_help_command()
        await self.notify_owner()
        self.add_sk_alias_for_jishaku()

    async def set_activity_to_help_command(self):
        await self.change_presence(
            activity=Activity(type=ActivityType.watching, name=HELP_COMMAND))

    async def notify_owner(self):
        await self.fetch_owner()
        await self.owner.send(TESTING_MSG if env.TESTING else PROD_MSG)
        print(LOGGED_IN, self.user)

    async def fetch_owner(self):
        await self.is_owner(self.user)
        self.owner = self.get_user(self.owner_id)

    def add_sk_alias_for_jishaku(self):
        jishaku = self.get_command('jishaku')
        self.all_commands['sk'] = jishaku