import discord.ext.test as dpytest
from jenna import Jenna
from discord.ext import commands
import pytest
import discord
from conftest import send_cmd, verify_message


@pytest.fixture
def external_cogs():
    return ['jishaku']


@pytest.fixture(autouse=True)
def setup_owner(bot, members):
    bot.owner_id = members[0].id


def verify_jsk():
    verify_message(contains='Module was loaded')




@pytest.fixture
def disable_startup_notif(mocker):
    mocker.patch.object(Jenna, 'notify_owner')



@pytest.mark.asyncio
async def test_custom_alias_sk(bot: Jenna, disable_startup_notif):
    await bot.on_ready()
    await send_cmd('sk')
    verify_jsk()