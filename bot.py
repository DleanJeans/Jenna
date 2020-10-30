import discord
import os
import colors
import env
import logging
import cogs

from discord.ext import commands
class Bot(commands.Bot):
    async def on_ready(self):
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="j help"))
        await self.is_owner(self.user)
        self.owner = self.get_user(self.owner_id)
        print('Logged in as', bot.user)
        if env.TESTING: return
        await self.owner.send('I\'m ready to go!')

intents = discord.Intents.default()
intents.members = True

prefixes = ['j ', 'jenna '] if not env.TESTING else ['k ']
for p in prefixes[::]:
    prefixes.append(p.capitalize())
bot = Bot(command_prefix=prefixes, case_insensitive=True, intents=intents)

if __name__ == '__main__':
    for cog in cogs.LIST:
        bot.load_extension(cog)
    bot.run(env.BOT_TOKEN)