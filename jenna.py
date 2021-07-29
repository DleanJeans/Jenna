import env

from discord import Activity, ActivityType
from discord.ext import commands

LOGGED_IN = 'Logged in as'
TESTING_MSG = 'Ready for testing!'
PROD_MSG = "Server restarted!"
HELP_COMMAND = 'j help'

TESTING_CHANNEL_ID = 664112170765910031


class Jenna(commands.Bot):
    async def on_ready(self):
        await self.set_activity_to_help_command()
        await self.notify_owner()
        self.add_sk_alias_for_jishaku()

    async def set_activity_to_help_command(self):
        await self.change_presence(activity=Activity(type=ActivityType.watching, name=HELP_COMMAND))

    async def notify_owner(self):
        await self.fetch_owner()
        if env.TESTING:
            testing_channel = self.get_channel(TESTING_CHANNEL_ID)
            await testing_channel.send(f'{self.owner.mention} {TESTING_MSG}')
        else:
            await self.owner.send(PROD_MSG)
        print(LOGGED_IN, self.user)

    async def fetch_owner(self):
        await self.is_owner(self.user)
        self.owner = self.get_user(self.owner_id)

    def add_sk_alias_for_jishaku(self):
        jishaku = self.get_command('jishaku')
        self.all_commands['sk'] = jishaku