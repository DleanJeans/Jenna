import env
import cogs
import pytest

from bot import create_bot
from discord.ext.test import configure, get_config, get_message, message, empty_queue


@pytest.fixture(autouse=True)
def disable_env_local_flags():
    env.LOCAL = False
    env.TESTING = False


@pytest.fixture
def cog_list():
    return []


@pytest.fixture
def external_cogs():
    return []


@pytest.fixture
async def bot(cog_list, external_cogs):
    bot = create_bot(cogs.get_full_path(cog_list) + external_cogs)
    configure(bot)
    yield bot
    await empty_queue()


@pytest.fixture()
def config():
    return get_config()


@pytest.fixture()
def guild(config):
    return config.guilds[0]


@pytest.fixture()
def channel(config):
    return config.channels[0]


@pytest.fixture()
def members(config):
    return config.members


async def send_cmd(*args):
    await message('j ' + ' '.join(args))


def verify_message(exact='', contains=''):
    msg = get_message()
    if exact:
        assert msg.content == exact
    elif contains:
        assert contains in msg.content
