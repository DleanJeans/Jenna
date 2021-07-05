import cogs
import pytest
import env

from bot import create_bot
from discord.ext.test import configure, get_config, get_message, message, empty_queue


@pytest.fixture(autouse=True)
def disable_env_local_flags():
    env.LOCAL = False
    env.TESTING = False


@pytest.fixture(autouse=True)
async def bot(cog_list, request):
    if 'nobot' in request.keywords:
        yield
        return
    bot = create_bot(cogs.get_full_path(cog_list))
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


async def send_cmd(*args):
    await message('j ' + ' '.join(args))


def verify_message(exact='', contains=''):
    msg = get_message()
    if exact:
        assert msg.content == exact
    elif contains:
        assert contains in msg.content
