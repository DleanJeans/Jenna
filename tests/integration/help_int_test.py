from discord.ext.test.runner import get_embed
import pytest
from conftest import verify_message
from discord.ext import commands
from discord.ext.test import message, verify

@pytest.fixture
def cog_list():
    return ['help']

@pytest.mark.asyncio
async def test_show_help_on_mention(bot:commands.Bot):
    await message(f'{bot.user.mention}')
    assert verify().message().embed()