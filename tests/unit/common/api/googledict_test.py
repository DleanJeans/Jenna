import pytest
from cogs.common.api.googledict import translate
from dotmap import DotMap
import requests_async


@pytest.mark.asyncio
@pytest.mark.enable_socket
async def test_auto_detect():
    result = await translate('lac')
    assert result.text == 'lake'


@pytest.mark.asyncio
@pytest.mark.enable_socket
async def test_lyric():
    result = await translate("En soirée appart', y'a deux types de dragueuse")
    assert result.text == "In the evening apartment, there are two types of flirt"


@pytest.mark.asyncio
@pytest.mark.enable_socket
async def test_one_character():
    result = await translate('a')
    print(result.data)


@pytest.mark.asyncio
@pytest.mark.enable_socket
async def test_request_api_and_parse():
    response = await requests_async.get(
        'https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl=auto&tl=en&q=bonjour')
    result = DotMap(response.json())
    text = result.sentences[0].trans
    src = result.src
    assert text == 'Hello'
    assert src == 'fr'