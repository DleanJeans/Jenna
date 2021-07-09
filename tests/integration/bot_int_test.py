from discord.ext.test.runner import get_message
import pytest
from conftest import verify_message
from discord.ext.test import message
from discord.ext import commands


@pytest.mark.asyncio
async def test_prefix():
    await message('j help')
    print(get_message(peek=True).content)
    verify_message()


@pytest.mark.asyncio
async def test_prefix_case_insensitive():
    await message('J help')
    print(get_message(peek=True).content)
    verify_message()


@pytest.mark.asyncio
async def test_mention_as_prefix(bot: commands.Bot):
    await message(f'{bot.user.mention} help')
    verify_message()
