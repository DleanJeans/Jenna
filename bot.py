import discord
import env
import cogs

from discord.ext import commands


class Bot(commands.Bot):
    async def on_ready(self):
        await bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching, name="j help"))
        await self.is_owner(self.user)
        self.owner = self.get_user(self.owner_id)
        print('Logged in as', bot.user)
        await self.owner.send(
            'Jennie is up and running' if env.TESTING else "I'm ready to go!")


def create_bot(cog_list, prefixes=['j ']):
    intents = discord.Intents.default()
    intents.members = True
    for p in prefixes[::]:
        prefixes.append(p.capitalize())
    bot = Bot(command_prefix=prefixes, case_insensitive=True, intents=intents)
    for cog in cog_list:
        bot.load_extension(cog)
    return bot


if __name__ == '__main__':
    prefixes = ['j ', 'jenna '] if not env.TESTING else ['jj ']
    bot = create_bot(cogs.LIST, prefixes)
    bot.run(env.BOT_TOKEN)