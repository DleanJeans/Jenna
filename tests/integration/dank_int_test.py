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
def dank_memer(guild):
    dank_memer = backend.make_user(DANK_MEMER, NUMBER, id_num=NUMBER)
    return backend.make_member(dank_memer, guild)


@pytest.fixture
async def send_as_dank_memer(dank_memer):
    async def send(text):
        return await message(text, member=dank_memer)

    return send


@pytest.mark.asyncio
async def test_dpytest_make_member(send_as_dank_memer):
    msg = await send_as_dank_memer('Scramble')
    assert msg.author.name == DANK_MEMER


@pytest.fixture
def assert_scramble(send_as_dank_memer):
    async def _assert_scramble(scrambled, expected):
        await send_as_dank_memer(f'Scramble - `{scrambled}`')
        assert expected in get_message().content

    return _assert_scramble


@pytest.mark.asyncio
async def test_unscramble_words_in_preset(assert_scramble):
    await assert_scramble('opiaripatn', 'apparition')
    await assert_scramble('mblata', 'matlab')
    await assert_scramble('icrhepn', 'pincher')
    await assert_scramble('aetsl', 'steal')
    await assert_scramble('dnima', 'admin')


@pytest.mark.asyncio
async def test_usb_scramble_wont_trigger_dank_memer(mocker):
    EXPECTED = 'scramble'
    SCRAMBLED = EXPECTED[::-1]
    mocker.patch('cogs.texts.texts.unscramble', return_value=[EXPECTED])

    await send_cmd('usb', SCRAMBLED)
    assert EXPECTED in get_message().content
    with pytest.raises(QueueEmpty):
        get_message()