import pytest
from asyncio.queues import QueueEmpty
from conftest import send_cmd
from discord.ext.test import backend, message, get_message


@pytest.fixture
def cog_list():
    return ['dank', 'texts']


DANK_MEMER = 'Dank Memer'
NUMBER = 5192


@pytest.fixture
def dank_memer(config, guild):
    dank_memer = backend.make_user(DANK_MEMER, NUMBER, id_num=NUMBER)
    return backend.make_member(dank_memer, guild)


@pytest.mark.asyncio
async def test_dpytest_make_member(bot, dank_memer):
    msg = await message('Scramble', member=dank_memer)
    assert msg.author.name == DANK_MEMER


@pytest.mark.asyncio
async def test_unscramble(bot, dank_memer):
    INPUT = 'opiaripatn'
    EXPECTED = 'apparition'

    await message(f'Scramble - `{INPUT}`', member=dank_memer)
    assert EXPECTED in get_message().content


@pytest.mark.asyncio
async def test_unscramble_unscramble_repeated(bot):
    EXPECTED = 'unscramble'
    SCRAMBLED = EXPECTED[::-1]

    await send_cmd(f'usb {SCRAMBLED}')
    assert EXPECTED in get_message().content
    with pytest.raises(QueueEmpty):
        get_message()