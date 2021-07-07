import discord
import env
import cogs

from discord.ext import commands
from jenna import Jenna

PROD_PREFIXES = ['j ', 'jenna ']
TEST_PREFIXES = ['jj ']


def create_bot(cog_list, prefixes=PROD_PREFIXES):
    intents = create_intents_for_fetching_members()
    prefixes = make_case_insensitive(prefixes)
    prefixes = commands.when_mentioned_or(*prefixes)
    bot = create_bot_with(prefixes, intents)
    load_cogs(bot, cog_list)
    return bot


def make_case_insensitive(prefixes):
    for p in prefixes[::]:
        prefixes.append(p.upper())
    return prefixes


def create_intents_for_fetching_members():
    intents = discord.Intents.default()
    intents.members = True
    return intents


def create_bot_with(prefixes, intents):
    apply_for_commands_only = True
    return Jenna(command_prefix=prefixes, intents=intents, case_insensitive=apply_for_commands_only)


def load_cogs(bot, cog_list):
    for cog in cog_list:
        bot.load_extension(cog)


def get_prefixes_for_env():
    return PROD_PREFIXES if not env.TESTING else TEST_PREFIXES


if __name__ == '__main__':
    prefixes = get_prefixes_for_env()
    bot = create_bot(cogs.LIST, prefixes)
    bot.run(env.BOT_TOKEN)