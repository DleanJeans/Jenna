import pytest
from conftest import verify_message
from discord.ext.test import message
from discord.ext import commands

@pytest.fixture
def cog_list():
    return []

@pytest.mark.asyncio
async def test_prefix():
    await message('j help')
    verify_message()

@pytest.mark.asyncio
async def test_mention_as_prefix(bot:commands.Bot):
    await message(f'{bot.user.mention} help')
    verify_message()