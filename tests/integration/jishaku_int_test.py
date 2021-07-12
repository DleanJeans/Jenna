import discord.ext.test as dpytest
from discord.ext.test.runner import get_message
from jenna import Jenna
from discord.ext import commands
import pytest
import discord
from conftest import send_cmd, verify_message


@pytest.fixture
def external_cogs():
    return ['jishaku']


@pytest.fixture(autouse=True)
def setup_owner(mocker):
    mocker.patch.object(Jenna, 'is_owner', return_value=True)


def verify_jsk():
    verify_message(contains='Module was loaded')


@pytest.mark.asyncio
@pytest.mark.slow
async def test_custom_alias_sk(bot: Jenna):
    bot.add_sk_alias_for_jishaku()
    await send_cmd('sk')
    verify_jsk()