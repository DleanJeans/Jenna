import pytest
from cogs.misc.google import GOOGLE_ICON
from common.googlesearch.googlesearch_async import GoogleExchangeResult, GooglePageResult
from discord.ext.test import message, get_embed
from unittest.mock import AsyncMock, patch


@pytest.fixture(scope='module')
def cog_list():
    return ['misc']


@pytest.fixture(autouse=True)
def setup_bot(bot, clean_up_bot):
    pass


class Duck:
    PAGE_TITLE = 'Duck - Wikipedia'
    PAGE_LINK = 'https://en.wikipedia.org/wiki/Duck'
    PAGE_PREVIEW = 'Duck is the common name for numerous species of waterfowl in the family Anatidae. Ducks are generally smaller and shorter-necked than swans and geese, ...'
    PAGE_EXTRA_LINKS = '[‎Domestic duck](https://en.wikipedia.org/wiki/Domestic_duck) · [‎Muscovy duck](https://en.wikipedia.org/wiki/Muscovy_duck) · [‎Mandarin duck](https://en.wikipedia.org/wiki/Mandarin_duck) · [‎Rubber duck](https://en.wikipedia.org/wiki/Rubber_duck)'
    PAGE_DESCRIPTION = f'[**{PAGE_TITLE}** (en.wikipedia.org)]({PAGE_LINK})\n{PAGE_PREVIEW}'


def patch_google(result):
    return patch('cogs.misc.google.search', new_callable=AsyncMock, return_value=[result])


@pytest.fixture
async def google_duck():
    result = GooglePageResult()
    result.title = Duck.PAGE_TITLE
    result.link = Duck.PAGE_LINK
    result.preview = Duck.PAGE_PREVIEW
    result.extra_links = Duck.PAGE_EXTRA_LINKS

    with patch_google(result):
        await message('j gg duck')
        return get_embed()


@pytest.mark.asyncio
async def test_google_duck(google_duck):
    assert google_duck.author.name == 'Google Search'
    assert google_duck.author.icon_url == GOOGLE_ICON

    assert google_duck.title == 'duck'
    assert google_duck.url == 'https://www.google.com/search?q=duck'
    assert google_duck.description == Duck.PAGE_DESCRIPTION


class FourTwenty:
    TITLE = '420 United States Dollar equals'
    PREVIEW = '9,669,240.00 Vietnamese dong'


@pytest.fixture
async def google_420_usd_to_vnd():
    result = GoogleExchangeResult()
    result.title = FourTwenty.TITLE
    result.preview = FourTwenty.PREVIEW

    with patch_google(result):
        await message('j gg 420 usd to vnd')
        return get_embed()


@pytest.mark.asyncio
async def test_convert_currency_display_no_parentheses(google_420_usd_to_vnd):
    embed = google_420_usd_to_vnd

    assert embed.description == f'**{FourTwenty.TITLE}**\n{FourTwenty.PREVIEW}'