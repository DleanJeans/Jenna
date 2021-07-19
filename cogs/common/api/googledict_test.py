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
async def test_lyric(similar):
    result = await translate("En soirée appart', y'a deux types de dragueuse")
    assert similar(result.text, 'In the evening apart, there are two types of flirt')


@pytest.mark.asyncio
@pytest.mark.enable_socket
async def test_one_character_no_error():
    await translate('a')


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


@pytest.mark.asyncio
@pytest.mark.enable_socket
async def test_chinese():
    result = await translate('既然我找不到你，那只有站在最显眼的地方让你来找', 'vi')
    assert result.text == 'Vì không tìm được em nên anh chỉ có thể đứng ở nơi dễ thấy nhất để em đến tìm'


@pytest.mark.asyncio
@pytest.mark.enable_socket
async def test_multiline(similar):
    result = await translate(
        '''In many countries today the eating habits and lifestyle of children are different from those of previous generations. Some people say this has had a negative effect on their health.
To what extent do you agree or disagree with this opinion?''', 'vi')
    EXPECTED = '''Ở nhiều nước hiện nay, thói quen ăn uống và lối sống của trẻ em khác với các thế hệ trước. Một số người nói rằng điều này đã ảnh hưởng xấu đến sức khỏe của họ.
Bạn đồng ý hay không đồng ý với ý kiến ​​này ở mức độ nào?'''
    assert similar(result.text, EXPECTED)
