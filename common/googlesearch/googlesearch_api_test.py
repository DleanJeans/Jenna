import pytest
from . import search


@pytest.fixture(scope='module')
async def google_duck():
    results = await search('duck')
    return results[0]


@pytest.mark.asyncio
@pytest.mark.enable_socket
async def test_title(google_duck):
    assert google_duck.title == 'Duck - Wikipedia'


@pytest.mark.asyncio
@pytest.mark.enable_socket
async def test_link(google_duck):
    assert google_duck.link == 'https://en.wikipedia.org/wiki/Duck'


@pytest.mark.asyncio
@pytest.mark.enable_socket
async def test_preview(google_duck):
    EXPECTED_PREVIEW = "Duck is the common name for numerous species of waterfowl in the family Anatidae. Ducks are generally smaller and shorter-necked than swans and geese, ..."
    assert google_duck.preview == EXPECTED_PREVIEW
    print(google_duck.preview)


@pytest.mark.asyncio
@pytest.mark.enable_socket
async def test_extra_links(google_duck):
    EXPECTED = '[Domestic duck](https://en.wikipedia.org/wiki/Domestic_duck) · ‎[Muscovy duck](https://en.wikipedia.org/wiki/Muscovy_duck) · ‎[Mandarin duck](https://en.wikipedia.org/wiki/Mandarin_duck) · ‎[Rubber duck](https://en.wikipedia.org/wiki/Rubber_duck)'
    assert google_duck.extra_links == EXPECTED


@pytest.mark.asyncio
@pytest.mark.enable_socket
async def test_convert_currency():
    result = await google_first_result('420 usd = vnd')
    assert result.title == '420 United States Dollar equals'
    assert 'Vietnamese dong' in result.preview
    assert not result.link
    assert not result.extra_links


async def google_first_result(query):
    results = await search(query)
    return results[0]


@pytest.mark.asyncio
@pytest.mark.enable_socket
async def test_stackoverflow_preview_only_2_lines():
    result = await google_first_result('python stringbuilder')
    assert result.preview.count('\n') == 1


@pytest.mark.asyncio
@pytest.mark.enable_socket
async def test_convert_temperature():
    result = await google_first_result('100 f = c')
    assert result.title == '100 Fahrenheit = 37.7778 Celsius'
    assert result.preview == '`Formula`: (100°F − 32) × 5/9 = 37.778°C'