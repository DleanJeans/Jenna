from discord.ext.test import backend
from discord.ext.test.runner import get_embed, get_message
import pytest

from conftest import send_cmd, verify_message


@pytest.fixture(scope='module')
def cog_list():
    return ['images']


@pytest.fixture(autouse=True)
def setup_bot(bot, clean_up_bot):
    pass


@pytest.mark.asyncio
async def test_self(me):
    await send_cmd_and_assert_user_avatar('', me)


async def send_cmd_and_assert_user_avatar(who, user):
    await send_cmd('ava ' + who)
    assert get_embed().image.url == str(user.avatar_url)


@pytest.mark.asyncio
async def test_mention(fuzzy):
    await send_cmd_and_assert_user_avatar(fuzzy.mention, fuzzy)


@pytest.mark.asyncio
async def test_fuzzy(fuzzy):
    await send_cmd_and_assert_user_avatar('Fuz', fuzzy)


@pytest.fixture
def fuzzy(make_member):
    return make_member('Fuzzy', 1000)


@pytest.mark.asyncio
async def test_send_slash_info_if_used_fuzzy_string(fuzzy):
    await send_cmd('ava fuz')
    msg = get_message()
    assert msg.embeds
    assert msg.content == '`/avatar` slash command is available!'