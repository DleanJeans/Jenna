import discord
import env
import cogs

from discord import Activity, ActivityType
from discord.ext import commands

LOGGED_IN = 'Logged in as'
TESTING_MSG = 'Jennie is up and running'
PROD_MSG =  "I'm ready to go!"
HELP_COMMAND = 'j help'

PROD_PREFIXES = ['j ', 'jenna ']
TEST_PREFIXES = ['jj ']

class Jenna(commands.Bot):
    async def on_ready(self):
        await self.set_activity_to_help_command()
        await self.notify_owner()

    async def set_activity_to_help_command(self):
        await self.change_presence(activity=Activity(type=ActivityType.watching, name=HELP_COMMAND))

    async def notify_owner(self):
        await self.fetch_owner()
        await self.owner.send(TESTING_MSG if env.TESTING else PROD_MSG)
        print(LOGGED_IN, bot.user)

    async def fetch_owner(self):
        await self.is_owner(self.user)
        self.owner = self.get_user(self.owner_id)

def create_bot(cog_list, prefixes=PROD_PREFIXES):
    intents = create_intents_for_fetching_members()
    prefixes = commands.when_mentioned_or(*prefixes)
    bot = create_bot_with(prefixes, intents)
    load_cogs(bot, cog_list)
    return bot

def create_intents_for_fetching_members():
    intents = discord.Intents.default()
    intents.members = True
    return intents

def create_bot_with(prefixes, intents):
    return Jenna(command_prefix=prefixes, case_insensitive=True, intents=intents)

def load_cogs(bot, cog_list):
    for cog in cog_list:
        bot.load_extension(cog)

def get_prefixes_for_env():
    return PROD_PREFIXES if not env.TESTING else TEST_PREFIXES

if __name__ == '__main__':
    prefixes = get_prefixes_for_env()
    bot = create_bot(cogs.LIST, prefixes)
    bot.run(env.BOT_TOKEN)