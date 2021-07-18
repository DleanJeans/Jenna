import pytest

from conftest import send_cmd, verify_message
from discord.ext.commands.errors import BadArgument
from discord.ext.test import get_embed
from googletrans.models import Translated
from urllib.parse import quote as urlquote

EMOJI = '<:emoji:12345>'


@pytest.fixture
def cog_list():
    return ['texts']


@pytest.fixture(autouse=True)
def setup_bot(bot):
    pass


mock_src = 'en'


@pytest.fixture(autouse=True)
async def mock_translator(mocker):
    global mock_src

    def mock_translate(origin, src, dest):
        src = mock_src if src == 'auto' else src
        text = 'hello' if origin == 'bonjour' else origin
        return Translated(src, dest, origin, text, pronunciation='', parts=[])

    from googletrans import Translator
    mocker.patch('cogs.common.api.googledict.translate', side_effect=mock_translate)

    yield
    mock_src = 'en'


def get_src_lang():
    return get_fields()[0].name


def get_dest_lang():
    return get_fields()[1].name


def get_src_text():
    return get_fields()[0].value


def get_dest_text():
    return get_fields()[1].value


def get_fields():
    return get_embed(peek=True).fields


@pytest.mark.asyncio
async def test_given_emoji_only__emoji_should_be_cleaned():
    CLEAN_EMOJI = ':emoji:'
    await send_cmd('str', EMOJI)
    verify_message(CLEAN_EMOJI)

    await send_cmd('tr', EMOJI)
    assert CLEAN_EMOJI in get_dest_text()


@pytest.mark.asyncio
async def test_given_text_with_emojis__emojis_should_be_removed():
    await send_cmd('str bonjour', EMOJI)
    verify_message('hello')


@pytest.mark.asyncio
async def test_zh_without_cn_should_be_corrected_to_zh_cn():
    await send_cmd('tr hello >zh')
    assert 'zh-cn' in get_dest_lang()


@pytest.mark.asyncio
async def test_zh_underscore_ch_should_be_corrected_to_zh_dash_cn():
    await send_cmd('tr hello >zh_cn')
    assert 'zh-cn' in get_dest_lang()


@pytest.mark.asyncio
async def test_given_en_text__should_translate_to_vi():
    await send_cmd('tr hello')
    assert 'vi' in get_dest_lang()


@pytest.mark.asyncio
async def test_should_raise_invalid_lang_code():
    with pytest.raises(BadArgument):
        await send_cmd('tr hello vn>')


@pytest.mark.asyncio
async def test_print_supported_langs_no_error():
    await send_cmd('tr lang')
    await send_cmd('tr langs')
    await send_cmd('str lang')
    await send_cmd('str langs')


@pytest.mark.asyncio
async def test_embed_displayed_horizontally():
    await send_cmd('tr bonjour fr>en')
    assert 'French (fr)' in get_src_lang()
    assert 'English (en)' in get_dest_lang()
    assert 'bonjour' in get_src_text()
    assert 'hello' in get_dest_text()


@pytest.mark.asyncio
async def test_url_should_not_have_lang_code_in_text_param():
    from_french = 'fr>'
    await send_cmd('tr lac', from_french)
    assert urlquote(from_french) not in get_embed().author.url


@pytest.mark.asyncio
async def test_zh_CN_no_error():
    global mock_src
    mock_src = 'zh-CN'
    await send_cmd('tr 既然我')


@pytest.mark.asyncio
async def test_full_language_name():
    await send_cmd('tr spanish> hola')
    assert 'Spanish (es)' in get_src_lang()