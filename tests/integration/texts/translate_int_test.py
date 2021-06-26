from discord.ext.test.runner import get_embed
from discord.ext.test.verify import verify
import pytest
from googletrans.models import Translated
from tests.integration.conftest import send_cmd, verify_message

EMOJI = '<:emoji:12345>'


@pytest.fixture
def cog_list():
    return ['texts']


import re
from cogs.texts.translate import EMOJI_REGEX


@pytest.mark.nobot
def test_emoji_simplifier_regex():
    assert re.sub(EMOJI_REGEX, r'\2', EMOJI) == ':emoji:'


@pytest.fixture
async def mock_translator(mocker):
    def mock_translate(origin, src, dest):
        if len(origin) <= 2:
            raise TypeError('Too short')
        text = 'hello' if origin == 'bonjour' else origin
        return Translated(src, dest, origin, text, pronunciation='', parts=[])

    from googletrans import Translator
    mocker.patch.object(Translator, 'translate', side_effect=mock_translate)


#send_cmd, verify_message
@pytest.mark.asyncio
async def test_emoji_only__emoji_cleaned(mock_translator):
    CLEAN_EMOJI = ':emoji:'
    await send_cmd('str', EMOJI)
    verify_message(CLEAN_EMOJI)

    await send_cmd('tr', EMOJI)
    assert get_embed().description == CLEAN_EMOJI


@pytest.mark.asyncio
async def test_text_with_emojis__emojis_removed(mock_translator):
    await send_cmd('str bonjour', EMOJI)
    verify_message('hello')


@pytest.mark.asyncio
async def test_origin(mock_translator):
    await send_cmd('tr bonjour')
    assert get_embed().fields[0].value == 'bonjour'