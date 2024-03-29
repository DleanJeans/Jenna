import asyncio
import cogs
import env
import pytest

from bot import create_bot
from difflib import SequenceMatcher
from discord.ext.test import backend, configure, get_config, get_message, message, empty_queue


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def make_member(guild):
    def make(username, discrim, avatar=None, id=-1, _guild=None):
        user = backend.make_user(username, discrim, avatar, id)
        return backend.make_member(user, _guild or guild)
    return make

@pytest.fixture
def similarity():
    return lambda a, b: SequenceMatcher(None, a, b).ratio()


@pytest.fixture
def similar(similarity):
    return lambda a, b, sim=95: similarity(a, b) >= sim / 100


@pytest.fixture(autouse=True)
def disable_env_local_flags():
    env.LOCAL = False
    env.TESTING = False


@pytest.fixture(scope='module')
def cog_list():
    return []


@pytest.fixture(scope='module')
def external_cogs():
    return []


@pytest.fixture(scope='module')
def bot(cog_list, external_cogs):
    bot = create_bot(cogs.get_full_path(cog_list) + external_cogs)
    configure(bot)
    return bot


@pytest.fixture
async def clean_up_bot():
    yield
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


@pytest.fixture()
def me(members):
    return members[0]


async def send_cmd(*args):
    await message('j ' + ' '.join(args))


def verify_message(exact='', contains=''):
    msg = get_message()
    if exact:
        assert msg.content == exact
    elif contains:
        assert contains in msg.content
