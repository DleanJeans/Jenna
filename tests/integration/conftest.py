import cogs
import pytest
import discord.ext.test as dpytest
import env

from bot import create_bot


@pytest.fixture(autouse=True)
def disable_env_local_flags():
    env.LOCAL = False
    env.TESTING = False


@pytest.fixture
def bot(cog_list):
    bot = create_bot(cogs.get_full_path(cog_list))
    dpytest.configure(bot)
    return bot


async def send_cmd(*args):
    await dpytest.message("j " + " ".join(args))

@pytest.fixture()
def config():
    return dpytest.get_config()


@pytest.fixture()
def guild(config):
    return config.guilds[0]