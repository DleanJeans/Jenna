import unicodedata

from bs4 import BeautifulSoup
from common import USER_AGENT_HEADERS
from requests import get
from aioify import aioify


def _search(query, num_results=10, lang='en', proxy=None):
    html = fetch_website(query, num_results, lang, proxy)
    return list(parse_results(html))


search = aioify(_search)

GOOGLE_URL_TEMPLATE = 'https://www.google.com/search?q={}&num={}&hl={}'


def fetch_website(query, num_results=10, language_code='en', proxy=None):
    escaped_query = query.replace(' ', '+')

    num_results += 1  # google returns nothing with num=1
    google_url = GOOGLE_URL_TEMPLATE.format(escaped_query, num_results, language_code)
    proxies = None
    if proxy:
        proxies = {'https': proxy} if proxy[:5] == 'https' else {'http': proxy}

    response = get(google_url, headers=USER_AGENT_HEADERS, proxies=proxies)
    response.raise_for_status()

    return response.text


class BaseGoogleResult:
    def __init__(self):
        self.link = ''
        self.title = ''
        self.preview = ''
        self.extra_links = ''

    def parse_html(self, html):
        pass

    @classmethod
    def is_this_type(html):
        return False


normalize = lambda text: unicodedata.normalize('NFKD', text)


class GooglePageResult(BaseGoogleResult):
    @staticmethod
    def is_this_type(html):
        link, title = GooglePageResult.find_link_and_title(html)
        return link and title

    @staticmethod
    def find_link_and_title(html):
        link_tag = html.find('a', href=True)
        return link_tag, link_tag.h3

    def parse_html(self, html):
        url_line, title_tag = GooglePageResult.find_link_and_title(html)

        self.link = url_line.get('href')
        self.title = title_tag.text

        preview_block = url_line.parent.next_sibling
        self.preview = '\n'.join(normalize(part.text) for part in preview_block if not part.a)

        extra_links_tag = preview_block.div.next_sibling
        if not extra_links_tag: return

        for link in extra_links_tag('a'):
            link.replace_with(f'[{link.text}]({link["href"]})')

        self.extra_links = extra_links_tag.text.strip('\u200e')


class GoogleExchangeResult(BaseGoogleResult):
    @staticmethod
    def is_this_type(html):
        return GoogleExchangeResult.find_exchange_tag(html)

    @staticmethod
    def find_exchange_tag(html):
        return html.find('div', {'data-exchange-rate': True})

    def parse_html(self, html):
        tag = GoogleExchangeResult.find_exchange_tag(html)
        self.title = tag.div.text
        self.preview = tag.div.next_sibling.text


class GoogleUnitConversionResult(BaseGoogleResult):
    @staticmethod
    def is_this_type(html):
        return html.select and html.input

    def parse_html(self, html):
        unit_type, src_unit, dest_unit = [option.text for option in html('option', selected=True)]
        src_value, dest_value = [box['value'] for box in html('input')]
        formula = html('td')[1].text.strip()

        self.title = f'{src_value} {src_unit} = {dest_value} {dest_unit}'
        self.preview = f'`Formula`: {formula}'


result_types = [GoogleExchangeResult, GoogleUnitConversionResult, GooglePageResult]


def parse_results(raw_html):
    soup = BeautifulSoup(raw_html, 'html.parser')
    result_block = soup.find_all('div', class_='g')
    for block in result_block:
        for ResultType in result_types:
            if ResultType.is_this_type(block):
                result = ResultType()
                try:
                    result.parse_html(block)
                    yield result
                except:
                    pass
                break