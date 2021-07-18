import pytest
from discord.ext import commands
from discord.ext.test import message, get_embed


@pytest.fixture
def cog_list():
    return ['help']


@pytest.mark.asyncio
async def test_show_help_on_mention(bot: commands.Bot):
    await message(f'{bot.user.mention}')
    assert get_embed()