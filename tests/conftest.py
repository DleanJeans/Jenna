import cogs
import pytest
from bot import create_bot
import discord.ext.test as dpytest


@pytest.fixture
def bot(cog_list):
    bot = create_bot(cogs.get_full_path(cog_list))
    dpytest.configure(bot)
    return bot


async def send(*args):
    await dpytest.message("j " + " ".join(args))
